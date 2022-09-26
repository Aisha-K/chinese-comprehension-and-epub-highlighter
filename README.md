# chinese-comprehension-and-epub-modifier
Analyze a Chinese text (using your known comprehension if you want) and modify an epub to highlight infrequnt words. Useful Chinese language learners when reading long texts.


## Core features
Analyze a Chinese text (.txt, .pdf, or .epub) to get:
  - the number of unique characters, total charactesrs, unique words
  - hsk breakdown
  - character frequency breakdown
    - a csv file exported of the number of times each charcatcer appears
    - how many characters appear less than 1 times, less then 2 times ... etc.
  - using your known words to gauge comprehension.

  Modify an epub to highlight characters that do not appear often (e.g. less than X times)

## Other features
- Count unique unknown words in text
- Calculate comprehension of text based on your known words
  - Calculate the above splitting text and known vocab word-by-word or character-by-character
- Exclude words such as proper nouns to improve comprehension accuracy 
- Output unknown words into a file, sorted by frequency
- Add all words from book to known wordlist

# Quickstart

## Requirements
- Install Python 3.9 (see detailed instuctions below if unsure how)
- Install the necessary python libraries by opening the cmd (type cmd in the folder path bar) int the main directory (containin the requirements file) and entering:
```
pip install -r requirements.txt
```

## Analyzer


1. From the main directory to run the analyzer. Run:
  
    ```
    python analyzer.py -t "./relative_path_to_book/book_name.epub"
    ```
  After the "-t" flag, the path to the epub (from the current directory) should be inputted (as shown above as an example)

2. Outputted word frequencies will be in the `./char_freqs_output` folder. The analyses will be shown in the cmd as: 
```
Total Words: 60900
Total Unique Words: 8450
Total Characters: 99800
Total Unique Characters: 2400

=== Freq of characters appearing less than X times: ===
  X    Count  % of total unique chars
---  -------  -------------------------
  1      429  18%
  2      679  28%
  3      831  35%
  4      972  40%
  5     1076  45%

=== HSK Breakdown ===
Level      Count  Cumulative Frequency
-------  -------  ----------------------
1          17235  (28.3%)
2           4629  (35.901%)
3           5180  (44.407%)
4           4156  (51.232%)
5           3765  (57.414%)
6           2262  (61.128%)
-          23673  (100.0%)
```

## Epub highlighter 

1. Run the anaylyzer first so the frequency csv is created
2. To run the epub modifier:

  ```
  python epub_highlighter.py --epub "./relative_path_to_book/book_name.epub" -  -f 3
  ```

  The "-f" flag is for the frequency to use to choose which characters to highlight. I.e. in the above eaxmple all caracters appearing 3 times or less will be highlighted.
  
  
  The modified epub will be in the same directory as the original.


# Built upon
This tool has been built upon:
- https://github.com/Destaq/chinese-comprehension : modified to get character freq breakdown; added epub support; all other features remain
- https://github.com/LordAmit/epub-highlighter: modified to work with chinese texts, cannot add definition



# Installation Guide for those unfamiliar with programming
*Non-technical explanation for those not familiar with programming.*

Step 1: Download Python 3.9 or below. [Link](https://www.python.org/downloads/release/python-3912/)

**Note program will not run on Python 3.10 or above**

Step 2: Install Python 3.9. When installing you need to make sure you click the box on the bottom that says "install path variable".

Step 3: After Python is installed click on the search bar and type cmd to start command prompt. This will pull up a window that is "Command Prompt" (Windows).

If you are using Mac, simply open a terminal window by pressing cmd-space and then typing terminal and opening said app.

Step 4: Verify you have python installed by typing `python --version`, it should tell you that you have python 3.X.X installed. If the version says 2.X.X, try typing `python3 --version` instead, and use `python3 -m pip` instead of `pip` in future steps.

Step 5: Download the comprehension zip file [here](https://github.com/Destaq/chinese-comprehension) by clicking the green button and clicking download zip.

Step 6: Once the comprehension zip file is installed you can extract it to where you want it to be.

Step 7: Open the command prompt/terminal window and navigate to the folder you extracted the comprehension zip file to. [How to navigate in the terminal tutorial](https://tutorials.codebar.io/command-line/introduction/tutorial.html). You can also navigate by dragging the folder to the command prompt.

Step 8: Type in `pip install -r requirements.txt` in the commmand line once you navigate to the comprehension folder.

Step 9: You can now refer to the documentation on this page to use the tool!

Finally (technical), note that if you are using an **M1 Mac**, you will need to run everything via a virtual environment as this chip is not supported yet by LAC. This can be easily done with conda by following the following [steps](https://github.com/conda-forge/miniforge/issues/165#issuecomment-860233092).




# Analyzer: Detailed Usage explanation
```
usage: comprehension.py [-h] -k KNOWN -t TARGET [-m MODE] [-u UNKNOWN]
                        [-e EXCLUDE]

Calculates percentage comprehension of a text file based on known words.

optional arguments:
  -h, --help            show this help message and exit
  -k KNOWN, --known KNOWN
                        Relative path to .txt file with newline-separated known words.
  -t TARGET, --target TARGET
                        Relative path to .txt target file in Chinese.
  -m MODE, --mode MODE  Mode for separating text and known vocab: 'smart' (default, word-by-word using jieba) 'simple' (character-by-character)
  -c, --characters      Add this flag (just -c, no extra info) if you know all the characters in your wordlist. This is due to segmentation limitation. For ex. 慢慢的 is seen as one word, if this word is not in your wordlist,
                        it will be unknown. By setting this flag (and having the characters 慢 and 的 in your wordlist (can be part of other words), 慢慢的 will be an 'understood' word.
  -u UNKNOWN, --unknown UNKNOWN
                        Path to output file with unknown words from text. Skip to not create an output file.
  -e EXCLUDE, --exclude EXCLUDE
                        Path to .txt file with newline-separated words to exclude (e.g. proper nouns)
```

## Target file (file to analyze, required)

The `--target` parameter takes the filename containing the target text. This should be normally formatted:
```
美猴王一見，倒身下拜，磕頭不計其數，口中只道：「師父，師父，我弟子志心
朝禮，志心朝禮。」祖師道：「你是那方人氏？且說個鄉貫、姓名明白，再拜。」
猴王道：「弟子乃東勝神洲傲來國花果山水簾洞人氏。」祖師喝令：「趕出去！
他本是個撒詐搗虛之徒，那裏
...
```


## Known words (optional)
The `--known` or `-k` parameter takes the filename containing known words. These words represent all words the user knows for best accuracy. Methods for fetching these words:
- export from Anki
- export from Pleco
- take HSK test
- consult [HelloChinese word list](https://docs.google.com/spreadsheets/d/1PppWybtv_ch5QMqtWlU4kAm08uFuhYK-6HGVnGeT63Y/edit#gid=121546596)

The file should have words separated line-by-line:
```
是
你好
再见
...
```

By doing so, and also outputting a file, any words/characters that you don't know will have a star symbol (*) by them.

## Comprehension flag (optional)

The -c or --comprehension flag allows you to mark words which would otherwise be unknown as known, as long as you know all of the characters that make it up. Due to the way the word segmenter words, many words that learners are likely to know are graded separately, and thus would not be present on the known.txt file.

See https://github.com/Destaq/chinese-comprehension#usage for details and examples

## Simple and smart mode (optional)

`--mode` allows you to switch between 'simple' and 'smart' mode, where the default is 'smart' - segmenting text word-by-word (ex. 你/有/什么/名字/？ for smart vs 你/有/什/么…… for simple.

## Output unkown words (optional)

`--unknown` allows you to create a file with all the unknown words in the text, in the format:
```
Hanzi : Count
Hanzi : Count
...
```

which is sorted by frequency. Ideal when preparing for a more difficult text or wanting to recap words. __This file has to be .txt. format__. Ex. `python3 comprehension.py -k "data/known.txt" -t "books/Earth_Vernes.pdf" -u "data/unknown_words.txt"`.

The `--exclude` parameter takes the filename containing words to exclude words. Exclude any proper nouns such as character names & company names to improve accuracy.

The file should have words separated line-by-line:
```
安琪
赵宁一
爱丽丝
麦当劳
...
```

### Example

*Code*: `python3 comprehension.py --known "known.txt" -t "samples/books/Great_Expectations.pdf" -u "output.txt"`
*Description*: Gathers known words from `known.txt`, and analyzes `samples/books/Great_Expectations.pdf` using the default word-by-word splitting. Unknown words are outputted to `output.txt`.

*Content of `output.txt`*
```
道 : 4621
行者 : 2575
來 : 1665
裏 : 1591
...
```


# Epub highlighter Detailed usage
The Epub Words Highlighter highlights all the words from a provided list of words as a csv file (can open in excel too to view). Give it a epub file (test/test.epub) and a file (list) containing list of words, and it will make them bold and italic for you in all the chapters, all the paragraphs.

The proper format is outputted automatically from the analyzer. It will be placed in the `/char_freqs_output/` folder and will be formatted as:
```
又, 1485
卻, 1264
```

This is useful for language learners so that they do not spend long trynig to memorize/search up words that will not appear again frequently in the book.

```
usage: epub_highlighter.py [-h] -e EPUB -f FREQ_LIMIT

Highlight text based on a word list

optional arguments:
  -h, --help            show this help message and exit
  -e EPUB, --epub EPUB  Relative path to .epub file.
  -f FREQ_LIMIT, --freq_limit FREQ_LIMIT
                        Number below which characters will boldened in the epub. Ex:
                        if 3, characters appearning 3 times or less times will be
                        boldened

```

# Vocab Adder
The `vocab_adder` file is extremely simple. It allows you to input a file and your known vocab list, and will append all unknown words in the file to your vocab list.

Example:
`python3 vocab_adder.py -t books/Earth_Vernes.pdf -k data/known.txt`

You can specify the mode (default is smart, which is segmentation) with the `-m` flag by typing `--mode simple`.

# FAQ

Q: How is punctuation counted?
A: As is the industry standard, punctuation (periods, commas, etc.) *are* included in total character count. However, they are not included in unique character count nor in any output files.
