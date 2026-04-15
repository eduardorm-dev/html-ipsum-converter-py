# Source - https://stackoverflow.com/a/35355433

import bs4
from emoji import is_emoji
import random

import argparse
from pathlib import Path

emojis = ['😊', '🚀', '🌟', '🎉', '🔥', '🤖', '👾', '🌈', '🍕', '🎸']

ipsum_base_texts = {
    'lorem_ipsum': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
    'sagan_ipsum': "A very small stage in a vast cosmic arena dream of the mind's eye two ghostly white figures in coveralls and helmets are softly dancing galaxies Flatland hearts of the stars? Courage of our questions a mote of dust suspended in a sunbeam Cambrian explosion paroxysm of global death made in the interiors of collapsing stars vanquish the impossible. Tunguska event extraordinary claims require extraordinary evidence inconspicuous motes of rock and gas descended from astronomers network of wormholes Orion's sword and billions upon billions upon billions upon billions upon billions upon billions upon billions.",
    'coffee_ipsum': 'French press robust whipped redeye, french press steamed, breve galão id rich bar. Aroma so decaffeinated cream so black foam skinny. Cinnamon, trifecta black, barista sugar cappuccino so robust organic. Skinny in, shop qui acerbic roast java. Saucer breve bar  coffee black turkish, froth instant latte half and half fair trade spoon. As crema, brewed con panna mug barista cup french press. Dark, decaffeinated ut robusta kopi-luwak iced single origin sweet beans arabica. Caramelization french press half and half sit, dark black single shot cortado java single origin.'
}

def main():
    args = process_arguments()

    with open(args.input_file) as inf:
        txt = inf.read()
        input_soup = bs4.BeautifulSoup(txt, 'html.parser')

    converter = HtmlIpsumConverter(input_soup, args.output_file, args.ipsum_type)

    converter.run()

def process_arguments():
    parser = argparse.ArgumentParser(
        description="Process an HTML file and output another HTML file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "input_file",
        type=Path,
        help="Path to the input HTML file"
    )
    parser.add_argument(
        "output_file",
        type=Path,
        nargs="?",
        default=None,
        help="Path to the output HTML file (default: input_file with .processed.html suffix)"
    )

    # String choices # TODO use
    parser.add_argument(
        "--ipsum_type",
        choices=["lorem_ipsum", "sagan_ipsum", "coffee_ipsum"],
        default="lorem_ipsum",
        help="Processing mode"
    )

    args = parser.parse_args()

    if args.output_file is None:
        args.output_file = args.input_file.with_suffix('.processed.html')
    
    print(f"Input:  {args.input_file}")
    print(f"Output: {args.output_file}")
    print(f"Ipsum type: {args.ipsum_type}")

    return args

class HtmlIpsumConverter:
    def __init__(
        self,
        input_soup: Path,
        output_file: Path,
        ipsum_type: str
    ):
        self.input_soup = input_soup
        self.output_file = output_file
        self.ipsum_type = ipsum_type

        self.output_soup = bs4.BeautifulSoup()
        self.output_context = []
        self.current_output_item = None
        self.items_to_navigate = []

    def run(self):
        self.ipsum_text = ipsum_base_texts[self.ipsum_type]
        self.lorem_ipsum_length = len(self.ipsum_text)
        self.lorem_index = 0

        self.items_to_navigate.append(self.input_soup.html)

        while len(self.items_to_navigate) > 0:
            input_tag = self.items_to_navigate.pop()
            if type(input_tag) == bs4.NavigableString:
                # self.process_item_text(input_tag)
                self.current_output_item.append(input_tag)

            elif type(input_tag) == bs4.element.Tag:
                self.process_item_tag(input_tag)

            elif type(input_tag) == str:
                self.process_end_tag()
                print('Close tag: ' + input_tag)
            
            elif type(input_tag) == bs4.element.Comment:
                pass
            else: # Stylesheets and others
                self.current_output_item.append(input_tag)
                print('unknown - ', type(input_tag))

        with open(self.output_file, "w") as outf:
            outf.write("<!DOCTYPE html>")
            outf.write(self.output_soup.prettify(formatter='html'))

    def process_item_text(self, input_tag):
        item_text = str(input_tag)
        print('Text: <' + item_text + '>')
        strip_text = item_text.strip()
        if not strip_text:
            return
        
        text_len = len(item_text)
        remaining_text_len = text_len

        replacing_text = ''

        skipReplacing = False

        if text_len <= 2 and is_emoji(item_text):
            remaining_text_len = 0
            replacing_text = random.choice(emojis)
            skipReplacing = True
        else:
            while remaining_text_len >= (self.lorem_ipsum_length - self.lorem_index):
                replacing_text += self.ipsum_text[self.lorem_index:self.lorem_ipsum_length] + ' '
                remaining_text_len -= (self.lorem_ipsum_length - self.lorem_index)
                self.lorem_index = 0
        
        expected_final_index = self.lorem_index + remaining_text_len
        while expected_final_index < self.lorem_ipsum_length:
            if self.ipsum_text[expected_final_index] == ' ':
                break
            expected_final_index += 1
        
        if not skipReplacing:
            replacing_text += self.ipsum_text[self.lorem_index:expected_final_index]
        
        if expected_final_index < self.lorem_ipsum_length and self.ipsum_text[expected_final_index] == ' ':
            expected_final_index += 1
        self.lorem_index = expected_final_index

        if self.lorem_index >= self.lorem_ipsum_length:
            self.lorem_index = self.lorem_index % self.lorem_ipsum_length

        if not skipReplacing:
            if strip_text[0].upper() == strip_text[0]:
                first_char = replacing_text[0]
                replacing_text = replacing_text.replace(first_char, first_char.upper(), 1)
            if replacing_text[-1] == ',' and self.is_next_item_end_tag():
                replacing_text = replacing_text[0:-1]

        print('New text: <' + replacing_text + '>')
        self.current_output_item.append(replacing_text)

    def is_next_item_end_tag(self):
        return type(self.items_to_navigate[-1]) == str

    def process_item_tag(self, input_tag):
        print('Tag: ' + str(input_tag.name))
        
        next_tag = self.output_soup.new_tag(input_tag.name)
        next_tag.attrs = input_tag.attrs

        if self.current_output_item:
            self.current_output_item.append(next_tag)

        children_items = list(input_tag.children)

        if not children_items:
            return
        
        # Reverse items before inserting to stack, to pop them in regular order
        children_items.reverse()
        if self.current_output_item:
            self.output_context.append(self.current_output_item)
        
        self.current_output_item = next_tag
        
        self.items_to_navigate.append(input_tag.name) # Signal to close tag
        for child in children_items:
            self.items_to_navigate.append(child)

    def process_end_tag(self):
        if self.output_context:
            parent_item = self.output_context.pop()
            parent_item.append(self.current_output_item)
            self.current_output_item = parent_item
        else:
            self.output_soup = self.current_output_item


if __name__ == "__main__":
    main()
