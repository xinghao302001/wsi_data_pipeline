import os
import glob
from pathlib import Path
import yaml
import argparse
from dataclasses import dataclass

import torch
import h5py
from transformers import BioGptTokenizer, BioGptConfig
from histogpt.models import HistoGPTForCausalLM, PerceiverResamplerConfig
from histogpt.helpers.inference import generate
from histogpt.helpers.patching import PatchingConfigs


@dataclass
class GenerationConfigs:
    model_path: str
    save_path: str
    tokenizer_path: str
    patching_model_name: str = "ctranspath"
    length: int = 256
    top_k: int = 20
    top_p: float = 0.7
    temp: float = 0.7


def generate_wsi_text_w_patch_and_prompt_embed(configs: dict):
    ## load configs
    patching_configs = PatchingConfigs(**configs["patching"])
    generation_configs = GenerationConfigs(**configs["generation"])
    ## load histopt
    histogpt = HistoGPTForCausalLM(BioGptConfig(), PerceiverResamplerConfig())
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    histogpt = histogpt.to(device)
    state_dict = torch.load(generation_configs.model_path, map_location=device)
    histogpt.load_state_dict(state_dict, strict=True)

    wsi_feat_dir = (
        Path(patching_configs.save_path)
        / "h5_files"
        / f"{patching_configs.patch_size}px_{generation_configs.patching_model_name}_{patching_configs.resolution_in_mpp}mpp_{patching_configs.downscaling_factor}xdown_normal"
    )

    tokenizer = BioGptTokenizer.from_pretrained(generation_configs.tokenizer_path)
    prompt = "Final diagnosis:"
    prompt_tensor = torch.tensor(tokenizer.encode(prompt)).unsqueeze(0).to(device)

    # os.makedirs(generation_configs.save_path, exist_ok=True)
    ## generate a text for each WSI
    final_res = []
    for file_path in glob.glob(os.path.join(wsi_feat_dir, "*.h5")):
        file_name = os.path.basename(file_path)
        prefix = file_name.split(".")[0]
        with h5py.File(file_path, "r") as wsi_h5_file:
            features = wsi_h5_file["feats"][:]
            features_tensor = torch.tensor(features).unsqueeze(0).to(device)
            output = generate(
                model=histogpt,
                prompt=prompt_tensor,
                image=features_tensor,
                length=generation_configs.length,
                top_k=generation_configs.top_k,
                top_p=generation_configs.top_p,
                temp=generation_configs.temp,
                device=device,
            )
            text = tokenizer.decode(output[0, 1:])

            txt_file_path = os.path.join(generation_configs.save_path, f"{prefix}.txt")
            with open(txt_file_path, "w") as txt_file:
                txt_file.write(text)
            final_res.append([prefix, text])
            print(f"Finish generating: {txt_file_path}")
    # ## aggregate all results
    # if generation_configs.is_aggregated:
    #     csv_file_path = os.path.join(generation_configs.save_path, "result.csv")
    #     with open(csv_file_path, mode="w", newline="", encoding="utf-8") as csv_file:
    #         csv_writer = csv.writer(csv_file)
    #         csv_writer.writerow(["WSI Name", "Generated Text"])
    #         csv_writer.writerows(final_res)
    #     print(f"final result.csv stored in: {csv_file_path}")


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("--config", dest="config", required=True)
    args = args_parser.parse_args()
    with open(args.config, "r") as file:
        config_dict = yaml.safe_load(file)
    generate_wsi_text_w_patch_and_prompt_embed(config_dict)
