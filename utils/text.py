
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
#from deep_translator import GoogleTranslator

#def translate_text(text, target_lang='en'):
 #   try:
  #      return GoogleTranslator(source='auto', target=target_lang).translate(text)
   # except Exception as e:
    #    return text  # fallback to original


#def compare_with_translation(text1, text2):
  
 #   translated1 = translate_text(text1)
  #  translated2 = translate_text(text2)

   # return int(SequenceMatcher(None, translated1, translated2).ratio() * 100)



def compare_text(html_file1, html_file2):
    with open(html_file1, 'r', encoding='utf-8') as f1, open(html_file2, 'r', encoding='utf-8') as f2:
        soup1 = BeautifulSoup(f1, 'html.parser')
        soup2 = BeautifulSoup(f2, 'html.parser')

    text1 = soup1.get_text(strip=True)
    text2 = soup2.get_text(strip=True)

    text_similarity = SequenceMatcher(None, text1, text2).ratio() * 100
#    if text_similarity < 10:
 #       text_similarity_translation = compare_with_translation(text1, text2)
  #      if text_similarity_translation > text_similarity:
   #         text_similarity = text_similarity_translation
        
    return text_similarity
