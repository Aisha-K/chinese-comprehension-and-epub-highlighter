import os
import argparse
import csv
from tabulate import tabulate
from collections import Counter
from re import compile as _Re
import core.shared as shared
import csv
import re

from epub_conversion.utils import open_book, convert_epub_to_lines
#from epub2txt import epub2txt
import xml.etree.ElementTree as ET



os.system("")

parser = argparse.ArgumentParser(
    description="Calculate unique words and character count of a text file - result is rounded to nearest 50"
)
parser.add_argument(
    "-k",
    "--known",
    required=False,
    help="Relative path to .txt file with newline-separated known words for *ing in output.",
)
parser.add_argument(
    "-t",
    "--target",
    required=True,
    help="Relative path to .txt target file in Chinese.",
)
parser.add_argument(
    "-o",
    "--output",
    required=False,
    help="Path to output file with all words & characters words from text. Skip to not create an output file.",
)
parser.add_argument(
    "-e",
    "--exclude",
    required=False,
    help="Path to .txt file with newline-separated words to exclude (e.g. proper nouns).",
)
parser.add_argument(
    "-n",
    "--no-words",
    dest="no_words",
    action="store_true",
    help="Setting this flag will mean that the tool does not segment words, so you will not have a calculating of # of words, # of unique words, and HSK breakdown. Can lead to a significant speedup, as segmentation takes approx. 1 minute per 1 million characters. Off by default. To set, simply add -n."
)

parser.set_defaults(no_words=False)
args = parser.parse_args()

_unicode_chr_splitter = _Re("(?s)((?:[\ud800-\udbff][\udc00-\udfff])|.)").split


def split_unicode_chrs(text):
    """
    Split a Chinese text character by character.

    Curtesy of `flow` on StackOverflow: https://stackoverflow.com/a/3798790/12876940
    """
    return [chr for chr in _unicode_chr_splitter(text) if chr]

def text_analyzer(
    knownfile: str, targetfile: str, outputfile: str, excludefile: str, no_words: bool = False
) -> str:
    try:
        known_words = shared.load_word_list_from_file(knownfile)
    except TypeError:
        known_words = []

    exclude_words = []
    if excludefile != None:
        exclude_words = shared.load_word_list_from_file(excludefile)

    # access text in .txt format
    if (targetfile.split('.')[-1]=='epub'):
        # try:
        #     #try to convert to string text with this
        #     target_text = epub2txt(targetfile)
        # except:

        #read in xml lines
        book = open_book(targetfile)
        lines = convert_epub_to_lines(book)
        stripped_lines = []
        for line in lines:
            try: #strip xml tags nd only keep text
                tree = ET.fromstring(line)
                stripped_lines.append(''.join(tree.itertext()))
            except:
                continue
            #stripped_lines.append( "".join(re.findall(r'[\u4e00-\u9fff]+', line)) ) #get chinese chars only (strips punctuation too)
        target_text= "".join(stripped_lines)
    else:    
        target_text = shared.text_setup(targetfile)
        #target_text =  "".join(re.findall(r'[\u4e00-\u9fff]+', target_text)) remove punction from count

    target_text_content = shared.text_clean_up(target_text)
    target_text_content = ''.join(shared.remove_exclusions(target_text_content, exclude_words))
    target_character_content = split_unicode_chrs(target_text_content)
    counted_target_character = Counter(shared.remove_exclusions(target_character_content, exclude_words))

    punctuations = (
        ",.:()!@[]+/\\！?？｡。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃《》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.?;﹔|.-·-*─\''\""
    )
    punctuations = [e for e in punctuations]
    # delete the elements in punctuations from counted_target Counter object
    for e in punctuations:
        del counted_target_character[e]

    low_freq_table = []
    for i in range(1,6):
        i_freq = len({ x: count for x, count in counted_target_character.items() if count <= i })
        pct = round(100*i_freq/len(counted_target_character) )
        low_freq_table.append([i, i_freq, f'{pct}%' ] )        

    #print words to csv with count
    epubname = targetfile.split('/')[-1].split('.')[0]
    with open(f'./char_freqs_output/{epubname}.csv', 'w',newline='', encoding='utf-8-sig') as f:  # You will need 'wb' mode in Python 2.x
        as_dict =  { x: count for x, count in counted_target_character.items() }
        writer = csv.writer(f)
        for row in as_dict.items():
            writer.writerow(row)

    total_unique_characters = len(counted_target_character)

    if not no_words:
        # import LAC for segmentation
        from LAC import LAC

        # initialize the parser
        print("Initializing parser...", end="\r")
        lac = LAC(mode='seg')
        print("Initializing parser... done\n")

        target_word_content = list(lac.run(target_text_content))
        stripped_target_word_content = shared.remove_exclusions(target_word_content, exclude_words, True)  # get rid of punctuation that inflates the word count
        counted_target_word = Counter(stripped_target_word_content)  # yes for getting rid of punctuations
        total_unique_words = len(counted_target_word)

        # calculate hsk distribution
        hsk_distribution = {}
        with open('data/hsk_list.csv', mode='r', encoding="utf8") as csv_file:
            rows = csv.reader(csv_file, delimiter=",")
            for row in rows:
                if row[0] != "hanzi":  # first row
                    hsk_distribution[row[0]] = {
                        "level": row[1],
                        "pinyin": row[2],
                        "meaning": row[3]
                    }

        hsk_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, "-": 0}
        for word in stripped_target_word_content:
            try:
                hsk_counts[int(hsk_distribution[word]["level"])] += 1
            except:
                hsk_counts["-"] += 1

        total_value = 0
        all_values = sum(hsk_counts.values())
        for (key, value) in hsk_counts.items():
            total_value += value
            percentage = round((total_value / all_values) * 100, 3)
            value = [str(value), f" ({percentage}%)"]
            hsk_counts[key] = value

        hsk_output = []
        for (key, value) in hsk_counts.items():
            hsk_output.append([key, value[0], value[1]])

    if outputfile is not None:
        try:
            with open(outputfile, "w+", encoding="utf8") as file:
                if not no_words:
                    file.write("=== All Unique Words ===\n")
                    total_count = sum(counted_target_word.values())
                    current_cumulative_count = 0
                    for ele, count in counted_target_word.most_common():
                        current_cumulative_count += count
                        if ele not in known_words:
                            ele = "*" + str(ele)
                        file.write(ele + (8 - len(ele)) * " " + ": " + str(count) + (7 - len(str(count))) * " " + ": " + 8 * " " + str(round((current_cumulative_count * 100) / total_count, 3)) + "%\n")

                    file.write("\n\n\n")
                file.write("=== All Unique Characters ===\n")
                total_count = sum(counted_target_character.values())
                current_cumulative_count = 0
                for ele, count in counted_target_character.most_common():
                    current_cumulative_count += count
                    if ele not in known_words:
                        ele = "*" + str(ele)
                    file.write(ele + (8 - len(ele)) * " " + ": " + str(count) + (7 - len(str(count))) * " " + ": " + 8 * " " + str(round((current_cumulative_count * 100) / total_count, 3)) + "%\n")
        except KeyError as ke:
            return ke
            
    if not no_words:
        return (
            "\nTotal Words: "
            + f"{shared.round_to_nearest_50(len(stripped_target_word_content))}"  # stripped as in no punctuations
            "\nTotal Unique Words: "
            + f"{shared.round_to_nearest_50(total_unique_words)}"
            "\nTotal Characters: "
            + f"{shared.round_to_nearest_50(len(target_text_content))}"
            "\nTotal Unique Characters: "
            + f"{shared.round_to_nearest_50(total_unique_characters)}"
            "\n\n=== Freq of characters appearing less than X times: ===\n"
            + tabulate(low_freq_table, headers=["X", "Count", "% of total unique chars"])
            + "\n\n=== HSK Breakdown ===\n"
            + tabulate(hsk_output, headers=["Level", "Count", "Cumulative Frequency"])
        )
    else:
        return (
            "Total Characters: "
            + f"{shared.round_to_nearest_50(len(target_text_content))}"
            "\nTotal Unique Characters: "
            + f"{shared.round_to_nearest_50(total_unique_characters)}"
        )

if __name__ == "__main__":
    print(text_analyzer(args.known, args.target, args.output, args.exclude, args.no_words))
