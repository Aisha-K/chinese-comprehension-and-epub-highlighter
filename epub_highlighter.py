'''
Oh, an attractive module description here.
'''
import argparse
import os
import shutil
import zipfile
#from gi.repository import Gtk
from xml.dom import minidom
from xml.etree import ElementTree as ET
import re
import distutils.archive_util
import core.shared as shared
import csv as csv


MIMETYPE_OPF = 'application/oebps-package+xml'
MEDIA_TYPE = 'application/xhtml+xml'
current_progress_in_percent = 0
counter = 0
DELIMITER = ',-,'



parser = argparse.ArgumentParser(
description="Highlight text based on a word list"
)
parser.add_argument(
"-e",
"--epub",
required=True,
help="Relative path to .epub file.",
)

parser.add_argument(
"-f",
"--freq_limit",
required=True,
type=int,
help="Number below which characters will boldened in the epub. Ex: if 3, characters appearning 3 times or less times will be boldened",
)

parser.set_defaults(no_words=False)
args = parser.parse_args()

def get_content_files(opf_path: str):
    opf_xml = minidom.parse(opf_path).documentElement
    xhtmls = []
    for element in opf_xml.getElementsByTagName('item'):
        # print(element.getAttribute("href"))
        if element.getAttribute("media-type") == MEDIA_TYPE:
            xhtmls.append(element.getAttribute("href"))
    return xhtmls
    # if element.getAttribute("media-type") is (MEDIA_TYPE):
    #     print(element.getAttribute("href"))


def read_container(extract_path: str)->str:
    container_xml = extract_path + "META-INF/container.xml"
    minidom_xml = minidom.parse(container_xml).documentElement
    opf_path = None
    for element in minidom_xml.getElementsByTagName('rootfile'):
        if element.getAttribute('media-type') == MIMETYPE_OPF:
            # Only take the first full-path available
            opf_path = element.getAttribute('full-path')
            break
    opf_path = extract_path + opf_path
    return opf_path
    # i = root.findall('./rootfile')
    # print(i[0].tag)


def highlight_content(content, word, meaning=None):
    global counter
    # insensitive_hippo = re.compile(re.escape('hippo'), re.IGNORECASE)
    # insensitive_hippo.sub('giraffe', 'I want a hIPpo for my birthday')
    word = str(word).strip()
    #word = ' ' + word + ' '
    if not meaning:
        highlighted_word = " <b><i>" + word + "</i></b> "
    else:
        highlighted_word = " <b><i>" + \
            word.upper() + "</i></b> [" + meaning.strip() + "] "
    # print(word, highlighted_word)
    # exit()
    
    #changed_content = content.encode('utf-8').replace( word.encode('utf-8'), highlighted_word.encode('utf-8') )
    changed_content = re.sub(word, highlighted_word, content)    #print(content[0:5])

    if content != changed_content:
        counter = counter + 1
    # print(content, changed_content)
    # exit()

    return changed_content


def read_contents(xml_path) -> str:
    return str(open(xml_path, "r", encoding='utf-8').read())


def read_list_of_words(list_path, freq_limit):
    list_below_limit = []
    print(list_path)
    #read in csv
    with open(list_path, encoding='utf-8') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        #get words below limit
        for row in spamreader:
            if(int(row[1]) <=freq_limit):
                list_below_limit.append(row[0])    

    return list_below_limit


# def read_list_of_words_with_meanings(list_path):
#     contents = open(list_path).readlines()
#     words = []
#     meanings = []
#     for content in contents:
#         # print(content)
#         split_content = str(content).split(DELIMITER)
#         words.append(split_content[0])
#         meanings.append(split_content[1])
#     return words, meanings


def write_content(xml_path, content):
    open(xml_path, mode='w', encoding='utf-8').write(content)


def do_something_with_progress(progress_in_hundred: int):
    print("Current Progress: " + str(progress_in_hundred))


def replace_xml_files(xmls_with_path, words, progress_bar=None, status_bar=None, meanings=None):
    global current_progress_in_percent
    xml_file_count = len(xmls_with_path)
    files_processed = 0
    for xml in xmls_with_path:
        # content = open(xml).read()
        # print("Processing: " + xml)
        xml_file_contents = read_contents(xml)
        # print(xml_file_contents)
        for i in range(0, len(words)):
            word = words[i]
            # print(word)
            if meanings:
                meaning = meanings[i]
                xml_file_contents = highlight_content(
                    xml_file_contents, word, meaning)
            else:
                xml_file_contents = highlight_content(
                    xml_file_contents, word)
            # print(xml_file_contents)
            write_content(xml, xml_file_contents)
        files_processed = files_processed + 1
        current_progress_in_percent = (files_processed / xml_file_count)
        msg = "processing " + os.path.basename(xml)
        # if status_bar and progress_bar:
        #     status_bar.push(1, msg)
        #     progress_bar.set_fraction(current_progress_in_percent)
        #     while Gtk.events_pending():
        #         Gtk.main_iteration()
        # do_something_with_progress(current_progress_in_percent)


def create_epub(extracted_epub_path, original_epub_path):
    original_epub_basename = os.path.split(original_epub_path)[1]
    original_epub_dir = os.path.split(original_epub_path)[0]
    # print(original_epub_dir)
    # print(original_epub_basename)
    new_epub_name = os.path.splitext(original_epub_basename)[
        0] + "_highlighted.epub"
    # print(new_epub_name)
    # print(extracted_epub_path)
    new_epub_path = original_epub_dir + "/" + new_epub_name
    # print(new_epub_path)
    zip_path = distutils.archive_util.make_archive(
        new_epub_name, format='zip', root_dir=extracted_epub_path)
    shutil.move(zip_path, new_epub_path + '.zip')
    os.rename(new_epub_path + '.zip', new_epub_path.replace('zip', ''))


def remove_extracted_directory(extract_root):
    import shutil
    shutil.rmtree(extract_root)


def extract_epub_to_tmp_directory(
        epub_path) ->str:
    epub_basename = os.path.basename(EPUB_PATH)
    temp_dir = os.path.split(EPUB_PATH)[
        0] + "/tmp-" + os.path.splitext(epub_basename)[0]
    # os.mkdir(temp_dir)
    # words = ["Test"]
    epub_file = zipfile.ZipFile(epub_path, mode='r')
    # print(epub_basename)
    extract_path = temp_dir + "/"
    # print(extract_path)
    epub_file.extractall(path=extract_path)
    return extract_path


def get_full_content_xmls_filepaths(extract_path):
    opf_path = read_container(extract_path)
    opf_path_base = os.path.split(opf_path)[0]

    xmls = get_content_files(opf_path)

    xmls_with_path = []
    for xml in xmls:
        xml_with_path = opf_path_base + '/' + xml
        xmls_with_path.append(xml_with_path)

    return xmls_with_path


def main(epub_path, list_path, freq_limit,  progress_bar=None, status_bar=None, with_meaning: bool = None):
    extract_path = extract_epub_to_tmp_directory(epub_path)
    xmls_with_path = get_full_content_xmls_filepaths(extract_path)
    if not with_meaning:
        texts = read_list_of_words(list_path, freq_limit)
        replace_xml_files(xmls_with_path, texts, progress_bar, status_bar)
    else:
        words, meanings = read_list_of_words_with_meanings(list_path)
        # print(words, meanings)
        replace_xml_files(xmls_with_path, words,
                          progress_bar, status_bar, meanings)
    create_epub(extract_path, epub_path)
    remove_extracted_directory(extract_path)
    global counter
    success_msg = "Complete! Highlighted " + \
        str(counter) + " Words in " + str(len(xmls_with_path)) + " files"
    if status_bar:
        status_bar.push(1, success_msg)
    else:
        print(success_msg)


if __name__ == '__main__':
    EPUB_PATH = args.epub
    EPUB_NAME = EPUB_PATH.split('/')[-1][0:-4]
    LIST_PATH =f"./char_freqs_output/{EPUB_NAME}csv"
    FREQ_LIMIT = args.freq_limit
    main(EPUB_PATH, LIST_PATH, FREQ_LIMIT, None, None, False )
