# document_scraping

Document Scraping is a package to scrape text/image based data from document containers. It uses various libraries to gain the capability of scraping a diverse set of documents. The output is a JSON file and a folder of images.

# Supported Document Formats
PDF, EPUB, MOBI, DOCX, TXT, DJVU.

# Requirements
DJVU format requires a specific 3rd party extension to be installed. For Windows it is:
DjVuLibre-3.5.28_DjView-4.12_Setup.exe (From: https://sourceforge.net/projects/djvu/files/)

!! Important Note: The installation path of the DjVuLibre should be added to the PATH environment variable. Otherwise, the script will not be able to find the library.


## Install Dependencies

```bash
pip install -r requirements.txt
```

# Usage

```bash
python main.py --source_dir <source_dir> --output_dir <output_dir> --mission_files_list <mission_files_list> --batch_count <batch_count>
```

## Parameters

* source_dir: Directory of the documents to be scraped. [Required]
* output_dir: Directory of the output files. [Necessary] [Default: output]
* batch_count: Number of documents to be scraped in a batch. [Necessary] [Default: 10]
* mission_files_list: JSON file containing the list of the documents to be scraped. [Optional] [Default: mission_files_list.json] 


