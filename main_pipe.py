import os
import glob
import csv
from pathlib import Path

import h5py
import torch
from transformers import BioGptTokenizer
from transformers import BioGptConfig
from histogpt.helpers.patching import main, PatchingConfigs
from histogpt.models import HistoGPTForCausalLM, PerceiverResamplerConfig
from histogpt.helpers.inference import generate

from config.configs import patching_configs, generation_configs

# Step 1: Generate embeddings for patches using CTranspath
patch_configs = PatchingConfigs(
    **patching_configs.dict(
        include={
            "slide_path",
            "save_path",
            "model_path",
            "patch_size",
            "white_thresh",
            "edge_threshold",
            "resolution_in_mpp",
            "downscaling_factor",
            "batch_size",
            "save_patch_images",
        }
    )
)


main(patch_configs)
# Step 2: Generate clinical reports using HistoGPT
histogpt = HistoGPTForCausalLM(BioGptConfig(), PerceiverResamplerConfig())
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
histogpt = histogpt.to(device)
state_dict = torch.load(generation_configs.model_path, map_location=device)
histogpt.load_state_dict(state_dict, strict=True)

wsi_feat_dir = (
    Path(patching_configs.save_path)
    / "h5_files"
    / f"{patching_configs.patch_size}px_{patching_configs.model_name}_{patching_configs.resolution_in_mpp}mpp_{patching_configs.downscaling_factor}xdown_normal"
)

tokenizer = BioGptTokenizer.from_pretrained(generation_configs.tokenizer_path)
prompt = "Final diagnosis:"
prompt = torch.tensor(tokenizer.encode(prompt)).unsqueeze(0).to(device)

final_res = []
# h5_files = glob.glob(os.path.join(save_dir, "*.h5"))
for file_path in glob.glob(os.path.join(wsi_feat_dir, "*.h5")):
    file_name = os.path.basename(file_path)
    prefix = file_name.split(".")[0]
    with h5py.File(file_path, "r") as wsi_h5_file:
        features = wsi_h5_file["feats"][:]
        features = torch.tensor(features).unsqueeze(0).to(device)
        output = generate(
            model=histogpt,
            prompt=prompt,
            image=features,
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

    print(f"finish generating: {txt_file_path}")

# Step 3: Aggregate all generated reports into a single CSV file
csv_file_path = os.path.join(generation_configs.save_path, "result.csv")
with open(csv_file_path, mode="w", newline="", encoding="utf-8") as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["WSI Name", "Generated Text"])
    csv_writer.writerows(final_res)

print(f"final result.csv stored in: {csv_file_path}")
