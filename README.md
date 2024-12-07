# WSI Data Pipeline 
Directory Structure
--------------------
    ├── HistoGPT
    ├── wsi_data_pipeline
    ├   ├── README.md
    ├   ├── .dvc  <- (optional) such files related to data version control is using dvc
    ├   ├── config  <- any .yml configuration files related to MLOps
    ├   ├── notebooks <- jupyter notebooks for demo experiments
    ├   ├── logs <- log files 
    ├   ├── model_checkpoints  <- checkpoints (.pth format) and related config files
    ├   │   ├── biogpt 
    ├   │   ├── ctranspath
    ├   │   ├── histogpt 
    ├   ├── data
    ├   │   ├── interim <- data in intermediate processing stage 
    ├   │   ├   ├── patches_and_embeds <- save generated patches and embeddings for WSIs
    ├   │   ├── processed <- data after all preprocessing has been done
    ├   │   ├   ├── wsi_texts <- save generated clinical reports for WSIs
    ├   │   ├   ├── result.csv <- aggrated all generated clinical reports in a .csv file.
    ├   │   └── raw <- original unmodified WSI images (.svs or .ndpi formats)
    ├   └── src
    ├   ├    ├── data <- scripts of data preparing and/or preprocessing
    ├   ├    ├── logger <- scripts of logging configs
    ├   ├    ├── evaluate <- scripts of evaluating model (#TODO)
    ├   ├    ├── pipelines <- scripts of pipelines (#TODO)
    ├   ├    ├── report <- scripts of visualization (often used in notebooks) (#TODO)
    ├   ├    ├── train <- scripts of training model (#TODO)
    ├   ├    └── utils.py <- auxiliary functions and classes (#TODO)
        

# Preparation
### 1. Create Conda `env`
```bashs
conda create -n wsi_data_pipeline python=3.10
```
### 2. Clone this repository
```bash
git clone https://github.com/marrlab/HistoGPT.git
cp -f wsi_data_pipeline/histogpt_install_setup/setup.py ./HistoGPT/setup.py
mv -f wsi_data_pipeline/histogpt_install_setup/requirements.txt /hy-tmp/wuxinghao/HistoGPT
```
### 3. Install related depencies for `env`
```bash
conda activate wsi_data_pipeline
cd HistoGPT
pip install .
pip install -r requirements.txt
```

### 4. Download WSI images
- Download different WSI image `zip` files, `unzip` them and get the WSI image in `.svs` format.
  - [Link for an eample](https://portal.gdc.cancer.gov/cases/0691b8c5-6244-407c-8601-fa1bda01ff2a?bioId=23ae363b-d19a-4ca9-8219-ca22eae68071)
- Change the `.svs` suffix into `.ndpi`.
- Store them into the `wsi_data_pipeline/data/raw` folder.


### 5. Initialize DVC init (Optional)

__1) Install DVC__ 
`pip install dvc`

[Link for installation instructions](https://dvc.org/doc/get-started/install)

__2) Initialize DVC init__

!! Before you initialize DVC, you must use `git init` to initialize the repository in `GitHub` that you want to use for DVC.

Initialize DVC 
```bash
cd wsi_data_pipeline
dvc init
```

Commit dvc init

```bash
git commit -m "Initialize DVC"
``` 

__3) Add remote storage for DVC (any cloud or local folder)__

[Link for Cloud Storage set-up](https://dvc.org/doc/user-guide/data-management/remote-storage)
```bash
# cd wsi_data_pipeline
dvc config cache.type copy
dvc remote add -d my_storage /tmp/dvc-storage # local-storage
```
__4) Add data fnder `DVC` management (any cloud or local folder)__

!! You can add any other data which you want them under `DVC` management.
```bash
dvc add data/raw/
## commit raw data to Git
git add data/raw.dvc .gitignore
git commit -m "Add raw data under DVC management"
## push data to remote storage
dvc push
```
# How to Work
## Run without `dvc`
__1) Set-up configs in the `config/wsi_data_pipe_config.yml` file.__

__2) Run with the followng `cmd`__:
```bash
cd wsi_data_pipeline
python src/pipelines/wsi_data_pipe.py --config config/wsi_data_pipe_config.yml
``` 
__3) The final generated clinic reports are `data/processed` folder, the on-demand generated patches are in the `data/interim/patches/` folder.__

## Run with `dvc`
### 1. Defining the Stages (Pipeline) with `CLI`
__1) Generate patches and embeddings__
```bash
dvc stage add -n generate_wsi_patches_and_embed \
  -d src/data/generate_wsi_patches_and_embed.py \
  -d config/wsi_data_pipe_config.yml \
  -d data/raw \
  python src/data/generate_wsi_patches_and_embed.py --config config/wsi_data_pipe_config.yml
```
this stage:
1) Generate embeddings and patches(optional) of each WSI using `CTranspath` model.
2) Store embeddings for text generation step in `data/interim/patches_and_embeds/h5_files` folder and patches (on demand) in `data/interim/patches_and_embeds/patches` folder.

Reproduce stage: `dvc repro --single-item generate_wsi_patches_and_embed`

__2) Generate Clinic Report Texts from generated WSI embeddings__
```bash
dvc stage add -n generate_wsi_text_with_patches_and_prompt_embeds \
  -d src/data/generate_wsi_texts.py \
  -d config/wsi_data_pipe_config.yml \
  python src/data/generate_wsi_texts.py --config config/wsi_data_pipe_config.yml
```
this stage:
1) Generate clinical reports for each WSI image using `prompt` embeddings and `patches` embeddings
2) Store each clinical in `data/processed/` folder within the name of `$wsi_name.txt`.
   
Reproduce stage: `dvc repro --single-item generate_wsi_patches_and_embed`

__3) Aggregate all generated Clinic Report Texts__
```bash
dvc stage add -n aggregate_all_wsi_texts \
  -d src/data/aggregate_all_wsi_texts.py \
  -d config/wsi_data_pipe_config.yml \
  -d data/processed/wsi_texts \
  python src/data/aggregate_all_wsi_texts.py --config config/wsi_data_pipe_config.yml
```
this stage:
Aggregates all WSI texts into a final summarized output. The results are persisted as the final processed data.

Reproduce stage: `dvc repro --single-item aggregate_all_wsi_texts`

### 2.Running the Pipeline
__1) View the pipeline structure and dependencies__
```bash
dvc dag
```
__2) Running the Entire Pipeline__
```bash
dvc repro
```
### 3. After Running, Data Sharing and Version Control
__1) Commit Pipeline Metadata to Git__
```bash
git add dvc.yaml dvc.lock
git commit -m "Add full WSI data pipeline with DVC"
```
__2) Push Data to Remote Storage__
```bash
dvc push
```
# Tutorial
### 1. All in Junyter Notebooks 
- run all in Jupyter Notebooks in `wsi_data_pipeline/notebooks` folder.

### 2. All related stages in `src` modules
- You can customize different pipelines within different modules as your wish in `.py` format, and store them in `pipelines` folder.

- Pipeline (python) scripts location: `src/pipelines`

### 3. All stages in `dvc.yaml` file
- You can directly write `dvc` stages in this `.yaml` file without `CLI`.
<!-- Main stages for `data` (WSI data pipeline):
* __generate_wsi_patches_and_embed.py__
    - Load config.yml and raw WSI images
    - Generate embeddings for the patches of the WSIs using `CTranspath` model
    - Store embeddings for text generation in `data/interim/patches_and_embeds/h5_files` folder and patches (on demand) in `data/interim/patches_and_embeds/patches` folder
* __generate_wsi_texts.py__
    - Generate clinical reports for each WSI image using `prompt` embeddings and `patches` embeddings
    - Store each clinical in `data/processed/` folder within the name of `$wsi_name.txt`.
* __aggregate_all_wsi_texts.py__
    - Aggregate all generation texts and store it into `data/processed/result.csv` file within the column names `[WSI Name, Generated Text]` -->







<!-- ### Step 4: Automate pipelines (DAG) execution  
- add pipelines dependencies under DVC control
- add models/data/congis under DVC control

__1) Prepare configs__

Run stage:
```bash
dvc run -f stage_prepare_configs.dvc \
        -d src/pipelines/prepare_configs.py \
        -d config/pipeline_config.yml \
        -o experiments/split_train_test_config.yml \
        -o experiments/featurize_config.yml \
        -o experiments/train_config.yml \
        -o experiments/evaluate_config.yml \
        python src/pipelines/prepare_configs.py \ 
            --config=config/pipeline_config.yml
```

Reproduce stage: `dvc repro pipeline_prepare_configs.dvc`


__2) Features extraction__

```bash
dvc run -f stage_featurize.dvc \
    -d src/pipelines/featurize.py \
    -d experiments/featurize_config.yml \
    -d data/raw/iris.csv \
    -o data/interim/featured_iris.csv \
    python src/pipelines/featurize.py \
        --config=experiments/featurize_config.yml
```


this pipeline:
1) creates new dataset with new features (`data/interim/featured_iris.csv`)
2) generates stage file `pipeline_featurize.dvc`

Reproduce stage: `dvc repro pipeline_featurize.dvc`

        
__3) Split train/test datasets__

Run stage:

```bash
dvc run -f stage_split_train_test.dvc \
    -d src/pipelines/split_train_test.py \
    -d experiments/split_train_test_config.yml \
    -d data/interim/featured_iris.csv \
    -o data/processed/train_iris.csv \
    -o data/processed/test_iris.csv \
    python src/pipelines/split_train_test.py \
        --config=experiments/split_train_test_config.yml \
        --base_config=config/pipeline_config.yml
```

this stage:

1) creates csv files `train_iris.csv` and `test_iris.csv` in folder `data/processed`
2) generates stage file `pipeline_split_train_test.dvc`        

Reproduce stage: `dvc repro pipeline_split_train_test.dvc`


__4) Train model__ 

Run stage:
```bash
dvc run -f stage_train.dvc \
    -d src/pipelines/train.py \
    -d experiments/train_config.yml \
    -d data/processed/train_iris.csv \
    -o models/model.joblib \
    python src/pipelines/train.py \
        --config=experiments/train_config.yml \
        --base_config=config/pipeline_config.yml
```


this stage:

1) trains and save model
2) generates stage file `pipeline_train.dvc`        

Reproduce stage: `dvc repro pipeline_train.dvc`


__5) Evaluate model__

Run stage:
```bash
dvc run -f stage_evaluate.dvc \
    -d src/pipelines/evaluate.py \
    -d experiments/evaluate_config.yml \
    -d models/model.joblib \
    -m experiments/eval.txt \
    python src/pipelines/evaluate.py \
        --config=experiments/evaluate_config.yml \
        --base_config=config/pipeline_config.yml
```    
    

this stage:

1) evaluate model
2) save evaluating report (metrics file `experiments/eval.txt`)
3) generate stage file `pipeline_evaluate.dvc`

Reproduce stage: `dvc repro pipeline_evaluate.dvc` -->



# References used for this tutorial

- [DVC tutorial](https://dvc.org/doc/tutorial) 