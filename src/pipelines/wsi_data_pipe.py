import os
import sys


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def wsi_data_pipe(configs: dict):
    logging.info("Starting: WSI patching and embedding generation...")
    generate_wsi_patches_and_embedding(configs)
    logging.info("Completed: Patching and embedding generation")

    logging.info("Starting: Clinical report text generation...")
    generate_wsi_text_w_patch_and_prompt_embed(configs)
    logging.info("Completed:Text generation.")

    logging.info("Starting: Text aggregation...")
    aggregate_all_generated_wsi_texts(configs)
    logging.info("Completed: Text aggregation.")


if __name__ == "__main__":
    import argparse
    import yaml
    import logging
    from datetime import datetime

    from src.logger.logger import LoggingSetup
    from src.data.generate_wsi_patches_and_embed import (
        generate_wsi_patches_and_embedding,
    )
    from src.data.generate_wsi_texts import generate_wsi_text_w_patch_and_prompt_embed
    from src.data.aggregate_all_wsi_texts import aggregate_all_generated_wsi_texts

    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger_config = LoggingSetup(
        log_file=f"logs/wsi_data_pipe_{current_time}.log",
        log_level="INFO",
        max_file_size=2 * 1024 * 1024,  # 2 MB
        backup_count=3,
    )
    logger_config.setup()

    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("--config", dest="config", required=True)
    args = args_parser.parse_args()
    with open(args.config, "r") as file:
        config_dict = yaml.safe_load(file)
    wsi_data_pipe(config_dict)
