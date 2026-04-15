# HtmlIpsumConverter py

This project consists on a python script that converts the text of an input HTML file by changing it to some 'ipsum', such as the Lorem-Ipsum, as well as other options.

I had the idea for this as I had another side project that dealt with HTML files, and wanted to convert some sample HTML files to remove the original context.

## Usage

First ensure you have the dependencies:

    ### You may also create a virtual env
    python -m venv converter-env
    source converter-env/bin/activate
    ###

    pip install bs4 emoji

`bs4` is for reading and writing HTML, and `emoji` is to analyse if some fields are emojis for specific treatment.

```
python html_ipsum_converter.py
                        [--ipsum_type {lorem_ipsum,sagan_ipsum,coffee_ipsum}]
                        input_file [output_file]
```

For example:

```
python html_ipsum_converter.py examples/document-original.html

python html_ipsum_converter.py proposal.html proposal2.html

python html_ipsum_converter.py flowers.html galaxies.html --ipsum_type sagan_ipsum
```

`input_file` is mandatory. `output_file`, if not provided, will be the same as `input_file` plus `'.processed'` before the extension. For example, `flowers.html` will produce `flowers.processed.html`.

`ipsum_type` is used to choose to which text should the content be converted. Default value is `lorem_ipsum`.

## Implementation

The script will take the HTML input and traverse all its tags and text data. For each piece of text, it will look at the chosen input, and find a fitting piece of text to replace it with.

For example, given the text "It defines the content and structure of web content", which is 51 characters long, it will look for 51 characters of the Ipsum, such as "Lorem ipsum dolor sit amet, consectetur adipiscing ". For the next piece of text, it will continue from the same point in the Ipsum text, and start over whenever reaching its end.

Take note of these cases as well:
- Whenever some text is replaced, the algorithm verifies if the original text started in upper case. If so, it uses upper case as well in the replaced text.
- If a node has a single character, the script will use the current char in the Ipsum text.
- If the text in a given node is just an emoji, it will replace it with another random emoji. This will not be done for regular text that contains emojis.
- If the algorithm intends to replace a text node with some Ipsum text ending in comma, it will remove such comma if the current tag is about to be closed, to avoid cases where there is a random comma without text to follow. But in cases where there is text and a following tag, it will keep it.
