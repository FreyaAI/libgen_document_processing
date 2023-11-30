from pathlib import Path
import os
import subprocess


class DocumentProcessor:
    def __init__(self, eos_labels=[".", "!", "?"], word_limit=1500):
        self.eos_labels = eos_labels
        self.word_limit = word_limit

    def extract_content(self, doc):
        """Scrapes headers & paragraphs from PDF and return texts with element tags.
        - doc: PDF document to iterate through --> type doc: <class 'fitz.fitz.Document'>
        - im_full_path: Full output path for the images
        - Returns: texts as a string
        """
        text_content = ""  # Text content
        first = True  # boolean operator for first header

        # img_id = 0 # Tracks number of images

        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:  # iterate through the text blocks
                if b["type"] == 0:  # this block contains text
                    block_string = ""  # text found in block

                    for l in b["lines"]:  # iterate through the text lines
                        for s in l["spans"]:  # iterate through the text spans
                            if s["text"].strip():  # removing whitespaces:
                                tmp_text = s["text"]
                                if first:
                                    first = False
                                    block_string = tmp_text
                                else:
                                    if block_string == "":
                                        # new block has started
                                        block_string = tmp_text
                                    else:  # in the same block, so concatenate strings
                                        if block_string[-1].isalpha():
                                            block_string += " " + tmp_text
                                        else:
                                            block_string += tmp_text

                    text_content += " " + block_string

                ## This part is removed for now, image extraction will be rediscussed
                ##
                ##elif b['type'] == 1: # This is an image block
                ##    img_ext = b['ext']
                ##    img_name = 'IMG_{0}.{1}'.format(img_id, img_ext)
                ##    img_full_path = im_full_path + '_' + img_name
                ##    img_data = b["image"]
                ##    img = PIL.Image.open(io.BytesIO(img_data))
                ##    img.save(open(img_full_path, 'wb'))
                ##    img_id += 1
                ##
                ##    text_content += " " + '<{0}>'.format(img_name)

        return text_content

    def concatenate_content(self, elements):
        """Concatenates consecutive elements of same tag if they are parts of the same sentence.
        - elements: Input list of extracted content with annotations
        - Returns Concatenated content as a list
        """

        output = []
        prev_element = ""
        prev_tag = ""
        for element in elements:
            tmp = element.find(">")

            if tmp < 0:
                output.append(prev_element)
                prev_element = ""
                prev_tag = ""
            elif tmp > 1:
                current_tag = element[1:tmp]
                current_content = element[tmp + 1 :]

                if current_tag == prev_tag and prev_tag.find("IMG") == -1:
                    tag_ind_prev = prev_element.find(">")
                    prev_content = prev_element[tag_ind_prev + 1 :]

                    if not prev_content:
                        prev_element = element
                        prev_tag = current_tag
                    elif not current_content:
                        output.append(prev_element)
                        prev_element = element
                        prev_tag = current_tag
                    else:
                        tmp_prev = prev_content.strip()[-1]
                        cond_1 = any(tmp_prev.find(x) > -1 for x in self.eos_labels)

                        if not cond_1:
                            tmp_cond_1 = prev_element[-1].isalpha()
                            tmp_cond_2 = current_content[0].isalpha()

                            if tmp_cond_1 and tmp_cond_2:
                                prev_element = prev_element + " " + current_content
                            else:
                                if prev_element[-1] == "-":
                                    prev_element = prev_element[0:-1] + current_content
                                else:
                                    prev_element += current_content
                        else:
                            output.append(prev_element)
                            prev_element = element
                            prev_tag = current_tag
                else:
                    output.append(prev_element)
                    prev_element = element
                    prev_tag = current_tag
            else:
                pass

        return output

    def count_words(self, input):
        return len(input.split())

    def concatenate_content_docx(self, elements):
        """Concatenates consecutive elements upto WORD_LIMIT num of words.
        - elements: Input list of extracted paragraphs
        - Returns Concatenated content as a list
        """

        output = []
        content = ""
        num_words = 0
        for element in elements:
            tmp = element.text
            tmp_content = tmp.strip()

            if num_words < self.word_limit:
                content += " " + tmp_content
                num_words += self.count_words(tmp_content)
            else:
                output.append(content)
                content = ""
                num_words = 0

        if num_words > 0:
            output.append(content)

        return output

    def divide_content(self, data):
        """Concatenates consecutive elements upto WORD_LIMIT num of words.
        - elements: Input list of extracted paragraphs
        - Returns Concatenated content as a list
        """

        output = []
        tmp_list = data.split()
        content = ""
        num_words = 0
        for tmp in tmp_list:
            tmp_content = tmp.strip()

            if num_words < self.word_limit:
                content += " " + tmp_content
                num_words += 1
            else:
                content += " " + tmp_content
                num_words += 1

                if any(tmp.find(x) > -1 for x in self.eos_labels):
                    output.append(content)
                    content = ""
                    num_words = 0

        if num_words > 0:
            output.append(content)

        return output

    def postprocess(self, elements, type):
        """Processes elements to filter unwanted content.
        - elements: Input list of extracted content with annotations
        - Returns Filtered content as alist
        """
        if type == "pdf":
            output = self.divide_content(elements)
        elif type == "epub" or type == "mobi":  # Handle list of lists
            output = self.divide_content(elements)
        elif type == "docx":
            output = self.concatenate_content_docx(elements)
        elif type == "txt" or type == "djvu":
            output = self.divide_content(elements)

        return output

    def read_DJVU(self, file_path):
        tmp_text_file = os.path.join(os.getcwd(), "tmp_djvu.txt")
        Path(tmp_text_file).touch(exist_ok=True)

        tmp_out = subprocess.run(["djvutxt", file_path, tmp_text_file])

        if tmp_out.returncode == 0:
            output = open(tmp_text_file).read()
        else:
            output = ""

        return output
