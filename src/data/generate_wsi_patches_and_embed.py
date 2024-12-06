import yaml
import argparse

from histogpt.helpers.patching import main as patching_main, PatchingConfigs


def generate_wsi_patches_and_embedding(configs: dict):
    pt_configs = configs["patching"]
    patch_configs = PatchingConfigs(**pt_configs)
    patching_main(patch_configs)


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("--config", dest="config", required=True)
    args = args_parser.parse_args()
    with open(args.config, "r") as file:
        config_dict = yaml.safe_load(file)
    generate_wsi_patches_and_embedding(config_dict)
