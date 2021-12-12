import multiprocessing.pool
from functools import reduce
import wikipedia
wikipedia.set_lang("sr")

specialCharacters = ['=', '-', ',', '!', '?', '.', '$', '(', ')', '[', ']', ';', '{', '}', '@', '#', '%', '^', '&', '*', '_', '+', '-', '/', '\\', '\'', '"', '<', '>', '|']

#'''Dohvata naslove zahtevanog broja stranica koje se pojavaljuju kao
#  rezultati pretrage za zadatu kljucnu rec'''
def get_pages(query, results=10): #staviti posle results = 50
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

def reduce_text(tuple, currentChar):
    array, flag = tuple
    if flag :
        return (array, flag)
    if len(array) >= 10_000 and currentChar == "$":
        flag = True
    return (array + list(currentChar), flag)


def prepare(tuple):
    query, string1 = tuple
    res = map(lower_case, str(string1))
    string2 = reduce(remove_special_chars, list(res), [])
    string3 = reduce(add_terminator, string2, []) #ukoliko imamo u stringu vise povezanih space-eva, stavice za svaki space $, da li je to validno?
    string3.append("$")
    string4, boolean = reduce(reduce_text, string3, ([], False))
    return query, string4

def choose_texts(tuple, currentElement): #uzima po pet tekstova za svaku kljucnu rec
    newArray, text, index, counter = tuple
    key, currentChar = currentElement
    previousKey, value = text[index-1]
    if key != previousKey:
        counter = 0
    if counter < 5:
        return (newArray + list(currentChar), text, index+1, counter+1)
    else:
        return (newArray, text, index+1, counter+1)
if __name__ == '__main__':
    keywords = ['Beograd', 'Prvi svetski rat', 'Protein', 'Mikroprocesor', 'Stefan Nemanja', 'Košarka']
    pool = multiprocessing.pool.ThreadPool(multiprocessing.cpu_count())
    titlesMatrix = pool.map(get_pages, keywords) #titlesMatrix = map(get_pages, keywords)-> za 2 sekunde sporije od map-a iz pool-a
    titlesList = reduce(append_list, titlesMatrix, [])

    #print(titlesList)
    processedText = pool.map(prepare, titlesList)

    print(processedText)

    chosenTexts, oldText, endIndex, cnt = reduce(choose_texts, processedText, ([], processedText, 0, 0))
    print(chosenTexts)


# stao sam kod zadatka 3, druga tacka




