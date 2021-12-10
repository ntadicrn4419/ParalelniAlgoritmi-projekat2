import multiprocessing.pool
from functools import reduce
import wikipedia
wikipedia.set_lang("sr")

specialCharacters = ['=', '-', ',', '!', '?', '.', '$', '(', ')', '[', ']', ';', '{', '}', '@', '#', '%', '^', '&', '*', '_', '+', '-', '/', '\\', '\'', '"', '<', '>', '|']

#'''Dohvata naslove zahtevanog broja stranica koje se pojavaljuju kao
#  rezultati pretrage za zadatu kljucnu rec'''
def get_pages(query, results=5): #staviti posle results = 50
  titles = wikipedia.search(query, results=results)
  pages = list()
  for title in titles:
      try:
          page = wikipedia.page(title)
          data = (query, page)
          pages.append(data)
      except:
          continue
  return pages

def append_list(array, currentElement):
    return array + currentElement

def lower_case(character):
    return str.lower(character)

def remove_special_chars(array, currentChar):
    if currentChar not in specialCharacters:
        return array + list(currentChar)
    else:
        return array

def add_terminator(array, currentChar):
        if currentChar == " " or currentChar == "\n" or currentChar == "\t":
            return array + list("$")
        else:
            return array + list(currentChar)

def reduce_text(array, currentChar):
    #if(len(array) >= 5 and currentChar == "$"): # umesto 5 staviti 10_000 posle
        #ovde sad nekako treba da osiguram da se ova funkcija vise ne poziva, tj. da reduce prekine sa radom. KAKO???
    return array + list(currentChar)


def prepare():
    string1 = "a aa!bbb! DA  DAd da $adsad) d (s" \
             "da sdS)"
    res = map(lower_case, string1)
    string2 = reduce(remove_special_chars, list(res), [])
    string3 = reduce(add_terminator, string2, []) #ukoliko imamo u stringu vise povezanih space-eva, stavice za svaki space $, da li je to validno?
    string3.append("$")

    string4 = reduce(reduce_text, string3[0:5], [])#umesto 5 staviti 10_000 posle; da li postoji nacin da se ogranici reduce tj. da se break-uje kada se ispuni neki uslov?

    print(string1)
    print(string2)
    print(string3)
    print(string4)

if __name__ == '__main__':
    #keywords = ['Beograd', 'Prvi svetski rat', 'Protein', 'Mikroprocesor', 'Stefan Nemanja', 'Košarka']
    #pool = multiprocessing.pool.ThreadPool(multiprocessing.cpu_count())
    #titlesMatrix = pool.map(get_pages, keywords, 5) #titlesMatrix = map(get_pages, keywords)-> za 2 sekunde sporije od map-a iz pool-a
    #titlesList = reduce(append_list, titlesMatrix, [])
    #print(titlesList)
    prepare()

#stao sam kod drugog zadatka, tacka 4.






