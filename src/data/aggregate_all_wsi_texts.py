import os
from pathlib import Path
import yaml
import argparse
import csv


def aggregate_all_generated_wsi_texts(configs: dict):
    aggregation_configs = configs["aggregation"]
    save_path = aggregation_configs["save_path"]
    texts_path = aggregation_configs["texts_path"]

    csv_file_path = os.path.join(save_path, "result.csv")
    final_res = []
    for report_file in Path(texts_path).glob("*.txt"):
        with open(report_file, "r") as file:
            final_res.append([report_file.stem, file.read()])

    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["WSI Name", "Generated Text"])
        csv_writer.writerows(final_res)

    print(f"Final result.csv stored in: {csv_file_path}")


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("--config", dest="config", required=True)
    args = args_parser.parse_args()
    with open(args.config, "r") as file:
        config_dict = yaml.safe_load(file)
    aggregate_all_generated_wsi_texts(config_dict)
