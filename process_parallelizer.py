import os
import multiprocessing

from tqdm import tqdm

from document import *


EXTENSION_TO_DOCUMENT = {
    "pdf": PDFDocument,
    "epub": EPUBDocument,
    "docx": DOCXDocument,
    "txt": TXTDocument,
    "djvu": DJVUDocument,
}


def get_document_by_extension(extension) -> Document:
    if extension not in EXTENSION_TO_DOCUMENT:
        return None

    return EXTENSION_TO_DOCUMENT[extension]


def extract_extension(filename):
    sections = filename.split(".")

    if len(sections) == 1:
        return None

    return sections[-1]


def extract_basefilename(filename):
    sections = os.path.basename(filename).split(".")

    if len(sections) == 1:
        return sections[0]

    return sections[-2]


def process(filename, output_directory):
    document_object = get_document_by_extension(extract_extension(filename))

    if document_object is None:
        return False

    document = document_object.fromPath(filename)

    if document is None:
        return False

    process_and_save_success = document.process_and_save(
        os.path.join(output_directory, extract_basefilename(filename) + ".parquet"),
        log=False,
    )

    return process_and_save_success


class DocumentProcessParallelizer:
    def __init__(self, output_directory):
        self.output_directory = output_directory

    def process(self, filenames):
        with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
            results = []

            for filename in tqdm(filenames, desc="Setting up processes"):
                result = pool.apply_async(
                    process, args=(filename, self.output_directory)
                )

                results.append(result)

            success_count = 0
            for result in tqdm(results, desc="Processing files"):
                if result.get():
                    success_count += 1

            print(f"Successfully processed {success_count} files")
