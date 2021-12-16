import multiprocessing.pool
from functools import reduce
from functools import partial
from numba import jit
import wikipedia

wikipedia.set_lang("en")  # staviti jezik da bude english, posto nam za srpski mesa cirilicu i latinicu

specialCharacters = ['=', '-', ',', '!', '?', '.', '$', '(', ')', '[', ']', ';', '{', '}', '@', '#', '%', '^', '&', '*',
                     '_', '+', '-', '/', '\\', '\'', '"', '<', '>', '|']
# '''Dohvata tekstove zahtevanog broja stranica koje se pojavljuju kao
#  rezultati pretrage za zadatu kljucnu rec'''
def get_pages(query, results=10):  # staviti posle results = 50
    titles = wikipedia.search(query, results=results)
    pages = list()
    for title in titles:
        try:
            page = wikipedia.page(
                title)  # ovo su samo naslovi stranica, ako zelimo tekst sa stranice: text = page.content

            text = page.content
            data = (query, text)

            # data = (query, page) # ovde dodajemo samo naslove stranica
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


def reduce_text(args, currentChar):
    array, flag = args
    if flag:
        return (array, flag)
    if len(array) >= 5000 and currentChar == "$":  # staviti posle na 10_000
        flag = True
    return (array + list(currentChar), flag)


def prepare(args):
    query, string1 = args
    res = map(lower_case, str(string1))
    string2 = reduce(remove_special_chars, list(res), [])
    string3 = reduce(add_terminator, string2,
                     [])  # ukoliko imamo u stringu vise povezanih space-eva, stavice za svaki space $, da li je to validno?
    string3.append("$")
    string4, boolean = reduce(reduce_text, string3, ([], False))
    return query, string4


def choose_texts(args,
                 currentElement):  # uzima po pet tekstova za svaku kljucnu rec; za sada ne bira nasumicno, nego za svaku kljucnu rec prvih 5 tekstova!
    newArray, text, index, counter = args
    key, currentChar = currentElement
    previousKey, value = text[index - 1]
    if key != previousKey:
        counter = 0
    if counter < 5:
        return (newArray + list(currentChar), text, index + 1, counter + 1)
    else:
        return (newArray, text, index + 1, counter + 1)


def create_tokens(args, currentChar):
    array, chosenTexts, index = args
    if index == len(chosenTexts) - 1 or currentChar == "$":
        return (array, chosenTexts, index + 1)
    token = currentChar + chosenTexts[index + 1]
    strings = []
    strings.append(token)
    return (array + strings, chosenTexts, index + 1)


def create_token_tuples(currentToken):
    return (currentToken, 1)


def reduce_token_tuples(args, currentTokenTuple):
    token, value = currentTokenTuple
    array, previousToken, index = args
    if token != previousToken:
        newTuple = (token, 1)
        helpArray = []
        helpArray.append(newTuple)
        return (array + helpArray, token, index + 1)
    else:
        copiedArray = array
        key, num = copiedArray[index]
        copiedArray[index] = (key, int(num) + 1)
        return (copiedArray, token, index)


def put_token(args, currentChar):
    tokenTuple, newText, originalText, index, sleep = args
    if (index < sleep):
        return (newText, tokenTuple, originalText, index + 1, sleep)
    token, value = tokenTuple
    if (currentChar in token):  # ovde i
        tmp = "".join(originalText[index: index + len(token)])  # ovde je bio problem
        tmp = tmp[0:len(token)]
        if (tmp == token):
            helpArray = []
            helpArray.append(token)
            return (newText + helpArray, tokenTuple, originalText, index + 1, index + len(token))
    helpArray = []
    helpArray.append(currentChar)
    return (newText + helpArray, tokenTuple, originalText, index + 1, 0)

#@jit
def insert_tokens_in_text(text, currentToken):
    # value je tekst koji se obradjuje
    key, value = text
    returnTuple = reduce(put_token, value, (currentToken, [], value, 0, 0))
    return (key, returnTuple[0])

def tokenize_all_texts(tokens, currentText):
    return reduce(insert_tokens_in_text, tokens, currentText)

#def tokens_in_text(tokens, textTuple): # textTuple je element niza newTexts
    #keyword, textValue = textTuple
    #sad za svaki token iz niza tokena tokens treba proveriti koliko puta se pojavljuje u datom tekstu(textValue)
    #return map(get_number_of_this_token, tokens)????

if __name__ == '__main__':

    keywords = ['Beograd', 'Prvi svetski rat', 'Protein', 'Mikroprocesor', 'Stefan Nemanja', 'Košarka']
    pool = multiprocessing.pool.ThreadPool(multiprocessing.cpu_count())
    titlesMatrix = pool.map(get_pages,
                            keywords)  # titlesMatrix = map(get_pages, keywords)-> za 2 sekunde sporije od map-a iz pool-a
    titlesList = reduce(append_list, titlesMatrix, [])
    processedText = pool.map(prepare, titlesList)
    returnTuple = reduce(choose_texts, processedText, ([], processedText, 0, 0))  # chosenTexts je lista karaktera
    chosenTexts = returnTuple[0]
    currentListOfTokens = []  # cemu bi ovo trebalo da sluzi?
    for i in range(2):  # staviti posle broj iteracija na 5000
        returnTuple = reduce(create_tokens, chosenTexts, ([], chosenTexts,0))  # returnTuple je samo promenljiva u koju pakujem povratnu vrednost reduce-a posto on vraca tuple.
        listOfCandidatesForNextToken = returnTuple[0]  # Uvek ce se na nultom indeksu nalaziti niz koji mi je dalje potreban; ostali elementi tuple-a su nebitni.

        tupleTokens = pool.map(create_token_tuples, listOfCandidatesForNextToken)
        sortedTupleTokens = sorted(tupleTokens, key=lambda tup: tup[0])
        returnTuple = reduce(reduce_token_tuples, sortedTupleTokens, ([], 0, -1))
        reducedTupleTokens = returnTuple[0]
        sortedReducedTupleTokens = sorted(reducedTupleTokens, key=lambda tup: tup[1], reverse=True)

        mostCommonToken = sortedReducedTupleTokens[0]
        currentListOfTokens.append(mostCommonToken)  # -> nije neophodno, ne koristi se nigde ta lista

        returnTuple = reduce(put_token, chosenTexts, (mostCommonToken, [], chosenTexts, 0, 0))
        chosenTexts = returnTuple[0]  # dodaje buffer ukoliko nije prazan

    tupleTokens = pool.map(create_token_tuples, chosenTexts)
    sortedTupleTokens = sorted(tupleTokens, key=lambda tup: tup[0])
    returnTuple = reduce(reduce_token_tuples, sortedTupleTokens, ([], 0, -1))
    reducedTupleTokens = returnTuple[0]
    sortedReducedTupleTokens = sorted(reducedTupleTokens, key=lambda tup: len(tup[0]), reverse=True)

    # tokeniziranje jednog teksta
    # print("UBACIVANJE TOKENA U NEKI TEKST")
    # newText1 = reduce(insert_tokens_in_text, sortedReducedTupleTokens, processedText[0])
    # print(sortedReducedTupleTokens)
    # print(processedText[0])
    # print(newText1)

    #tokeniziranje svih tekstova
    newTexts = pool.map(partial(tokenize_all_texts, sortedReducedTupleTokens), processedText)# newTexts je lista taplova gde je key kljucna rec, a value je niz tokena(i karaktera, ali i samo jedan karakter sada posmatrama kao token)



