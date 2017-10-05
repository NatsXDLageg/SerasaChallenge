import urllib.request
import re
import unicodedata
import sys
import string
import nltk
from bs4 import BeautifulSoup

#Lista de palavras-chave da operação 'Lava Jato', cada uma contendo uma pontuação baseada na especificidade da palavra com o assunto eem questão (a palavras mais genéricas é atribuída uma nota menor)
keywordScoreList = {
    "operação": 3, "operações": 2,
    "empreiteira": 2, "empreiteiras": 2, "empreiteiro": 2, "empreiteiros": 2,
    "petrobrás": 4, "petróleo": 3,
    "investigação": 1, "investigações": 1, "investigar": 1,
    "réu": 1, "réus": 1,
    "cartel": 5, "cartéis": 5,
    "doleiro": 2, "doleiros": 2,
    "corrupção": 5, "corrupções": 5,
    "licitação": 2, "licitações": 2,
    "crime": 1, "crimes": 1, "criminal": 1, "criminoso": 1, "criminosos": 1, "criminosa": 1, "criminosas": 1,
    "condenar": 2, "condenou": 2, "condenaram": 2, "condenado": 2, "condenados": 2, "condenada": 2, "condenadas": 2,
    "julgar": 2, "julgado": 2, "julgados": 2, "julgada": 2, "julgadas": 2,
    "prisão": 2, "prisões": 2,
    "propina": 3, "propinas": 3,
    "desvio": 2, "desvios": 2, "desviar": 2, "desvia": 2, "desviam": 2, "desviava": 2, "desviavam": 2,
    "intermediar": 1, "intermediário": 1, "intermediários": 1,
    "tribunal": 2, "tribunais": 2,
    "lavagem": 2, "lavagens": 2,
    "ilegal": 2, "ilegais": 2,
    "delegacia": 2, "delegacias": 2,
    "intimação": 2, "intimações": 2,
    "acusado": 2, "acusados": 2, "acusada": 2, "acusadas": 2, "acusação": 2, "acusações": 2,
    "delação": 3, "delações": 3, "delatado": 3, "delatados": 3, "delatada": 3, "delatadas": 3,
    "leniência": 3, "leniências": 3,
    "jurídico": 2, "jurídicos": 2, "juiz": 2,
    "executivo": 2, "executivos": 2,
    "legislativo": 2, "legislação": 2,
    "político": 2, "políticos": 2, "política": 2, "políticas": 2,
    "fiscal": 2, "fiscais": 2,
    "usufrutuário": 5, "usufrutuários": 5,
    "repatriado": 4, "repatriados": 4, "repatriação": 4,
    "deflagrado": 3, "deflagrados": 3, "deflagrada": 3, "deflagradas": 3,
    "catilinária": 5, "catilinárias": 5,
    "peculato": 5, "peculatos": 5,
    "fraudar": 3, "fraudatório": 3, "fraudatória": 3, "fraude": 3, "fraudes": 3,
    "foro": 3,
    "stf": 3, "tribunal": 3, "tribunais": 3
}

#Lista de nomes envolvidos na Lava Jato, retirada de https://pt.wikipedia.org/wiki/Lista_de_pessoas_envolvidas_na_Opera%C3%A7%C3%A3o_Lava_Jato
mainNamesRegexAreaList = {
    "Adir Assad": (r"Adir.*Assad", "empresarial"),
    "Aécio Neves": (r"A[eé]cio.*Neves", "política"),
    "Afonso Hamm": (r"Afonso.*Hamm", "política"),
    "Agenor Franklin Magalhães Medeiros": (r"Agenor.*(?:Franklin|Magalh[aã]es|Medeiros)", "empresarial"),
    "Aguinaldo Ribeiro": (r"Aguinaldo.*Ribeiro", "política"),
    "Alexandre Portela Barbosa": (r"Alexandre.*(?:Portela|Barbosa)", "judicial"),
    "Alberto Elísio Vilaça Gomes": (r"Alberto.*(?:El[ií]sio|Vila[cç]a|Gomes)", "empresarial"),
    "Aldemir Bendine": (r"Aldemir.*Bendine", "política"),
    "Alexandrino de Salles Ramos de Alencar": (r"Alexandrino.*(?:de Salles|Ramos|de Alencar)", "empresarial"),
    "Aline Corrêa": (r"Aline.*Corr[eê]a", "política"),
    "André Catão de Miranda": (r"Andr[eé].*(?:Cat[aã]o|de Miranda)", "empresarial"),
    "André Vargas": (r"Andr[eé].*Vargas", "política"),
    "Angelo Alves Mendes": (r"Angelo.*(?:Alves|Mendes)", "empresarial"),
    "Ângela Palmeira Ferreira": (r"[AÂ]ngela.*(?:Palmeira|Ferreira)", "política"),
    "Aníbal Gomes": (r"An[ií]bal.*Gomes", "política"),
    "Antonio Almeida da Silva": (r"Antonio.*(?:Almeida|da Silva)", "empresarial"),
    "Antonio Anastasia": (r"Antonio.*Anastasia", "política"),
    "Antonio Carlos Pieruccini": (r"Antonio.*(?:Carlos|Pieruccini)", "judicial"),
    "Antônio Pedro Campello de Souza Dias": (r"Ant[oô]nio.*(?:Campello|de Souza|Dias)", "empresarial"),
    "Armando Furlan Júnior": (r"Armando.*(?:Furlan|J[uú]nior)", "empresarial"),
    "Antonio Palocci": (r"Antonio.*Palocci", "política"),
    "Arthur Lira": (r"Arthur.*Lira", "política"),
    "Benedito de Lira": (r"Benedito.*de Lira", "política"),
    "Carlos Magno Ramos": (r"Carlos.*(?:Magno|Ramos)", "política"),
    "Cândido Vaccarezza": (r"C[aâ]ndido.*Vaccarezza", "política"),
    "Cesar Ramos Rocha": (r"Cesar.*(?:Ramos|Rocha)", "empresarial"),
    "Ciro Nogueira": (r"Ciro.*Nogueira", "política"),
    "Cristiano Kok": (r"Cristiano.*Kok", "empresarial"),
    "Dalton dos Santos Avancini": (r"Dalton.*(?:dos Santos|Avancini)", "empresarial"),
    "Daniela Leopoldo e Silva Facchini": (r"Daniela.*(?:Leopoldo e Silva|Facchini)", "empresarial"),
    "Dario de Queiroz Galvão": (r"Dario.*(?:de Queiroz|Galv[aã]o)", "empresarial"),
    "Delcídio do Amaral": (r"Delc[ií]dio.*do Amaral", "política"),
    "Dilceu Sperafico": (r"Dilceu.*Sperafico", "política"),
    "Dilma Rousseff": (r"Dilma.*Rousseff", "política"),
    "Edison Lobão": (r"Edison.*Lob[aã]o", "política"),
    "Ednaldo Alves da Silva": (r"Ednaldo.*(?:Alves|da Silva)", "empresarial"),
    "Eduardo Cunha": (r"Eduardo.*Cunha", "política"),
    "Eduardo da Fonte": (r"Eduardo.*da Fonte", "política"),
    "Eduardo de Oliveira Freitas Filho": (r"Eduardo.*(?:de Oliveira|Freitas|Filho)", "empresarial"),
    "Eduardo Vaz da Costa Musa": (r"Eduardo.*(?:Vaz|da Costa|Musa)", "empresarial"),
    "Erton Medeiros Fonseca": (r"Erton.*(?:Medeiros|Fonseca)", "empresarial"),
    "Elton Negrão de Azevedo Júnior": (r"Elton.*(?:Negr[aã]o|de Azevedo|J[uú]nior)", "empresarial"),
    "Flávio Gomes Machado Filho": (r"Fl[aá]vio.*(?:Gomes|Machado|Filho)", "empresarial"),
    "Flávio Sá Motta Pinheiro": (r"Fl[aá]vio.*(?:S[aá]|Motta|Pinheiro)", "empresarial"),
    "Fernando Antonio Guimarães Horneaux de Moura": (r"Fernando.*(?:Antonio|Guimar[aã]es|Horneaux|de Moura)", "política"),
    "Fernando Bezerra Coelho": (r"Fernando.*(?:Bezerra|Coelho)", "política"),
    "Fernando Collor de Mello": (r"Fernando.*(?:Collor|de Mello)", "política"),
    "Fernando Pimentel": (r"Fernando.*Pimentel", "política"),
    "Flávio David Barra": (r"Fl[aá]vio.*(?:David|Barra)", "empresarial"),
    "Gerson Almada": (r"Gerson.*Almada", "empresarial"),
    "Gladson Cameli": (r"Gladson.*Cameli", "política"),
    "Gleisi Hoffmann": (r"Gleisi.*Hoffmann", "política"),
    "Guido Mantega": (r"Guido.*Mantega", "política"),
    "Humberto Costa": (r"Humberto.*Costa", "política"),
    "Ildefonso Colares Filho": (r"Ildefonso.*(?:Colares|Filho)", "empresarial"),
    "Ivan Vernon Gomes Torres Júnior": (r"Ivan.*(?:Vernon|Gomes|Torres|J[uú]nior)", "política"),
    "Jaques Wagner": (r"Jaques.*Wagner", "política"),
    "Jean Alberto Luscher Castro": (r"Jean.*(?:Alberto|Luscher|Castro)", "empresarial"),
    "Jerônimo Goergen": (r"Jer[oô]nimo.*Goergen", "política"),
    "João Leão": (r"Jo[aã]o.*Le[aã]o", "política"),
    "João Alberto Pizzolati": (r"Jo[aã]o.*(?:Alberto|Pizzolati)", "política"),
    "Joesley Batista": (r"Joesley.*Batista", "empresarial"),
    "José Adolfo Pascowitch": (r"Jos[eé].*(?:Adolfo|Pascowitch)", "empresarial"),
    "João Procópio de Almeida Prado": (r"Jo[aã]o.*(?:Proc[oó]pio|de Almeida|Prado)", "empresarial"),
    "José Antunes Sobrinho": (r"Jos[eé].*(?:Antunes|Sobrinho)", "empresarial"),
    "José Dirceu de Oliveira e Silva": (r"Jos[eé].*(?:Dirceu|de Oliveira e Silva)", "política"),
    "José Humberto Cruvinel Resende": (r"Jos[eé].*(?:Humberto|Cruvinel|Resende)", "empresarial"),
    "José Linhares": (r"Jos[eé].*Linhares", "política"),
    "José Mentor": (r"Jos[eé].*Mentor", "política"),
    "José Otávio Germano": (r"Jos[eé].*(?:Ot[aá]vio|Germano)", "política"),
    "João Vaccari Neto": (r"Jo[aã]o.*(?:Vaccari|Neto)", "política"),
    "Júlio César dos Santos": (r"J[uú]lio.*(?:C[eé]sar|dos Santos)", "empresarial"),
    "Lázaro Botelho": (r"L[aá]zaro.*Botelho", "política"),
    "Roberto Britto": (r"Roberto.*Britto", "política"),
    "Lindberg Farias": (r"Lindberg.*Farias", "política"),
    "Lucélio Roberto von Lechten Góes": (r"Luc[eé]lio.*(?:Roberto|von Lechten|G[oó]es)", "empresarial"),
    "Luis Carlos Heinze": (r"Luis.*(?:Carlos|Heinze)", "política"),
    "Luiz Argôlo": (r"Luiz.*Arg[oô]lo", "política"),
    "Luiz Eduardo de Oliveira e Silva": (r"Luiz.*(?:Eduardo|de Oliveira e Silva)", "empresarial"),
    "Luiz Fernando Faria": (r"Luiz.*(?:Fernando|Faria)", "política"),
    "Luiz Inácio Lula da Silva": (r"Luiz.*(?:In[aá]cio|Lula|da Silva)", "política"),
    "Luiz Fernando Pezão": (r"Luiz.*(?:Fernando|Pez[aã]o)", "política"),
    "Marcelo Bahia Odebrecht": (r"Marcelo.*(?:Bahia|Odebrecht)", "empresarial"),
    "Márcio Farias da Silva": (r"M[aá]rcio.*(?:Farias|da Silva)", "empresarial"),
    "Mário Negromonte": (r"M[aá]rio.*Negromonte", "política"),
    "Mário Negromonte Júnior": (r"M[aá]rio.*(?:Negromonte|J[uú]nior)", "política"),
    "Michel Temer": (r"Michel.*Temer", "política"),
    "Milton Pascowitch": (r"Milton.*Pascowitch", "empresarial"),
    "Missionário José Olímpio": (r"Mission[aá]rio.*(?:Jos[eé]|Ol[ií]mpio)", "política"),
    "Nelson Meurer": (r"Nelson.*Meurer", "política"),
    "Olavo Horneaux de Moura Filho": (r"Olavo.*(?:Horneaux|de Moura|Filho)", "política"),
    "Otávio Marques de Azevedo": (r"Ot[aá]vio.*(?:Marques|de Azevedo)", "empresarial"),
    "Othon Zanoide de Moraes Filho": (r"Othon.*(?:Zanoide|de Moraes|Filho)", "empresarial"),
    "Otto Garrido": (r"Otto.*Garrido", "empresarial"),
    "Paulo Bernardo": (r"Paulo.*Bernardo", "política"),
    "Paulo Sérgio Boghossian": (r"Paulo.*(?:S[eé]rgio|Boghossian)", "empresarial"),
    "Pedro Corrêa": (r"Pedro.*Corr[eê]a", "política"),
    "Pedro José Barusco Filho": (r"Pedro.*(?:Barusco|Filho)", "empresarial"),
    "Pedro Henry": (r"Pedro.*Henry", "política"),
    "Renan Calheiros": (r"Renan.*Calheiros", "política"),
    "Renato Molling": (r"Renato.*Molling", "política"),
    "Renato de Souza Duque": (r"Renato.*(?:de Souza|Duque)", "empresarial"),
    "Ricardo Ribeiro Pessoa": (r"Ricardo.*(?:Ribeiro|Pessoa)", "empresarial"),
    "Roberto Balestra": (r"Roberto.*Balestra", "política"),
    "Roberto Marques": (r"Roberto.*Marques", "política"),
    "Roberto Teixeira": (r"Roberto.*Teixeira", "política"),
    "Rogério Cunha de Oliveira": (r"Rog[eé]rio.*(?:Cunha|de Oliveira)", "empresarial"),
    "Rogério Santos de Araújo": (r"Rog[eé]rio.*(?:Santos|de Araújo)", "empresarial"),
    "Romero Jucá": (r"Romero.*Juc[aá]", "política"),
    "Roseana Sarney": (r"Roseana.*Sarney", "política"),
    "Sandes Júnior": (r"Sandes.*J[uú]nior", "política"),
    "Sérgio Cunha Mendes": (r"S[eé]rgio.*(?:Cunha|Mendes)", "empresarial"),
    "Simão Sessim": (r"Sim[aã]o.*Sessim", "política"),
    "Valdir Lima Carreiro": (r"Valdir.*(?:Lima|Carreiro)", "política"),
    "Valdir Raupp": (r"Valdir.*Raupp", "política"),
    "Vander Loubet": (r"Vander.*Loubet", "política"),
    "Vilson Covatti": (r"Vilson.*Covatti", "política"),
    "Waldir Maranhão": (r"Waldir.*Maranh[aã]o", "política"),
    "Walmir Pinheiro Santana": (r"Walmir.*(?:Pinheiro|Santana)", "empresarial"),
    "Jorge Luiz Zelada": (r"Jorge.*(?:Luiz|Zelada)", "empresarial"),
    "Hamylton Pinheiro Padilha": (r"Hamylton.*(?:Pinheiro|Padilha)", "empresarial"),
    "Raul Schmidt Felippe Junior": (r"Raul.*(?:Schmidt|Felippe|Junior)", "empresarial"),
    "João Augusto Rezende Henriques": (r"Jo[aã]o.*(?:Augusto|Rezende|Henriques)", "empresarial"),
    "Hsin Chi Su (Nobu Su)": (r"(?:Hsin.*(?:Chi|Su)|Nobu.*Su)", "empresarial"),
    "Othon Luiz Pinheiro da Silva": (r"Othon.*(?:Pinheiro|da Silva)", "empresarial"),
    "Ana Cristina da Silva Toniolo": (r"Ana.*(?:da Silva|Toniolo)", "empresarial"),
    "Rogério Nora": (r"Rog[eé]rio.*Nora", "empresarial"),
    "Clóvis Renato": (r"Cl[oó]vis.*Renato", "empresarial"),
    "Olavinho Ferreira Mendes": (r"Olavinho.*(?:Ferreira|Mendes)", "empresarial"),
    "José Antunes Sobrinho": (r"Jos[eé].*(?:Antunes|Sobrinho)", "empresarial"),
    "Carlos Eduardo Strauch Albero": (r"Carlos.*(?:Strauch|Albero)", "empresarial"),
    "Enivaldo Quadrado": (r"Enivaldo.*Quadrado", "empresarial"),
    "Luiz Roberto Pereira": (r"Luiz.*Pereira", "empresarial"),
    "Newton Prado Júnior": (r"Newton.*(?:Prado|J[uú]nior)", "empresarial"),
    "Paulo Roberto Costa": (r"Paulo.*(?:Roberto|Costa)", "empresarial"),
    "Waldomiro de Oliveira": (r"Waldomiro.*de Oliveira", "empresarial"),
    "Alberto Youssef": (r"Alberto.*Youssef", "empresarial"),
    "Nestor Cerveró": (r"Nestor.*Cerver[oó]", "empresarial"),
    "Carlos Alberto Pereira da Costa": (r"Carlos.*(?:Pereira|da Costa)", "empresarial"),
    "Carlos Habib Chater": (r"Carlos.*(?:Habib|Chater)", "empresarial"),
    "Cleverson Coelho de Oliveira": (r"Cleverson.*(?:Coelho|de Oliveira)", "empresarial"),
    "Ediel Viana da Silva": (r"Ediel.*(?:Viana|da Silva)", "empresarial"),
    "Eduardo Hermelino Leite": (r"Eduardo.*(?:Hermelino|Leite)", "empresarial"),
    "Esdra de Arantes Ferreira": (r"Esdra.*(?:de Arantes|Ferreira)", "empresarial"),
    "Faiçal Mohamed Nacirdine": (r"Faiçal.*(?:Mohamed|Nacirdine)", "empresarial"),
    "Fernando 'Baiano' Antônio Falcão Soares": (r"Fernando.*(?:Falc[aã]o|Soares)", "empresarial"),
    "Fernando Augusto Stremel Andrade": (r"Fernando.*(?:Stremel|Andrade)", "empresarial"),
    "Iara Galdino da Silva": (r"Iara.*(?:Galdino|da Silva)", "empresarial"),
    "Jayme Alves de Oliveira Filho": (r"Jayme.*(?:Alves|de Oliveira|Filho)", "empresarial"),
    "João Ricardo Auler": (r"Jo[aã]o.*(?:Ricardo|Auler)", "empresarial"),
    "José Aldemário Pinheiro Filho": (r"Jos[eé].*(?:Aldem[aá]rio|Pinheiro|Filho)", "empresarial"),
    "José Ricardo Nogueira Breghirolli": (r"Jos[eé].*(?:Nogueira|Breghirolli)", "empresarial"),
    "Juliana Cordeiro de Moura": (r"Juliana.*(?:Cordeiro|de Moura)", "empresarial"),
    "Julio Gerin de Almeida Camargo": (r"Julio.*(?:Gerin|de Almeida|Camargo)", "empresarial"),
    "Leonardo Meirelles": (r"Leonardo.*Meirelles", "empresarial"),
    "Luccas Pace Júnior": (r"Luccas.*(?:Pace|J[uú]nior)", "empresarial"),
    "Márcia Danzi Russo Corrêa de Oliveira": (r"M[aá]rcia.*(?:Danzi|Russo|Corr[eê]a|de Oliveira)", "empresarial"),
    "Marcio Andrade Bonilho": (r"Marcio.*(?:Andrade|Bonilho)", "empresarial"),
    "Maria Dirce Penasso": (r"Maria.*(?:Dirce|Penasso)", "empresarial"),
    "Mário Lúcio de Oliveira": (r"M[aá]rio.*de Oliveira", "empresarial"),
    "Matheus Coutinho de Sá Oliveira": (r"Matheus.*(?:Coutinho|de S[aá]|Oliveira)", "empresarial"),
    "Nelma Mitsue Penasso Kodama": (r"Nelma.*(?:Mitsue|Penasso|Kodama)", "empresarial"),
    "Pedro Argese Junior": (r"Pedro.*(?:Argese|Junior)", "empresarial"),
    "Rafael Ângulo Lopez": (r"Rafael.*(?:[AÂ]ngulo|Lopez)", "empresarial"),
    "Renê Luiz Pereira": (r"Ren[eê].*(?:Luiz|Pereira)", "empresarial"),
    "Rinaldo Gonçalves de Carvalho": (r"Rinaldo.*(?:Gon[cç]alves|de Carvalho)", "empresarial"),
    "Augusto Ribeiro de Mendonça Neto": (r"Augusto.*(?:Ribeiro|de Mendon[cç]a|Neto)", "empresarial"),
    "Dario Teixeira Alves Júnior": (r"Dario.*(?:Teixeira|Alves|J[uú]nior)", "empresarial"),
    "Mario Frederico Mendonça Góes": (r"Mario.*(?:Frederico|Mendon[cç]a|G[oó]es)", "empresarial"),
    "Sônia Mariza Branco": (r"S[oô]nia.*(?:Mariza|Branco)", "empresarial"),
    "Leon Denis Vargas Ilário": (r"Leon.*(?:Denis|Vargas|Il[aá]rio)", "empresarial"),
    "Ricardo Hoffmann": (r"Ricardo.*Hoffmann", "empresarial"),
    "Murilo Tena Barros": (r"Murilo.*(?:Tena|Barros)", "empresarial"),
    "Sérgio Cabral": (r"S[eé]rgio.*Cabral", "política")
}

baseScore = 0.0005

#Função que remove acentos de textos
def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def main():
    url = input("Por favor digite a url para o website: ")

    pageContent = ""
    try:
        print("Recuperando o arquivo html, por favor aguarde...")

        #urllib: usada para recuperar a página web para a url dada
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req)
        pageContent = str(resp.read().decode('utf-8').strip())
    except (urllib.error.URLError, urllib.error.HTTPError):
        print("Error with given URL, quitting...")
        return

    print("Analisando html")

    #BeautifulSoup: usada para parsear o arquivo web e retornar os conteúdos do mesmo em formato texto
    soup = BeautifulSoup(pageContent, 'html.parser')
    print("Recuperando conteúdo dentro do html\n")
    pageText = soup.get_text()
    pageTextCharacterCount = len(pageText)

    #re: usada para diversas validações usando expressões regulares, dentre elas, dividir o conteúdo da página em uma lista de palavras em letra minúscula e sem acento
    allPageWords = re.findall(r"[\w']+", pageText)
    allPageWordsInLowerCase = [strip_accents(x.lower()) for x in allPageWords]
    
    score = 0
    for keyword in keywordScoreList.keys():
        occurrences = allPageWordsInLowerCase.count(strip_accents(keyword.lower()))
        if occurrences > 0:
            score += (keywordScoreList[keyword] * occurrences)

    normalizedScore = score / pageTextCharacterCount
    if normalizedScore > baseScore:
        print("Status: url válida - o website dado possui assunto 'Lava Jato'!")
        print("Procurar-se-á agora pelas pessoas envolvidas mencionadas:")

        #Regex usada para tentar encontrar nomes completos
        allPossibleBRFullnames = re.findall(r"[A-ZÀÁÂĖÈÉÊÌÍÒÓÔÕÙÚÛÇ][a-zàáâãèéêìíóôõùúç]+(?:[ ](?:das?|dos?|de|da|do|e|[A-Z][a-zàáâãèéêìíóôõùúç]+(?:'[A-ZÀÁÂĖÈÉÊÌÍÒÓÔÕÙÚÛÇ]?[a-zàáâãèéêìíóôõùúç]+)?))+", pageText)
        for mainName in mainNamesRegexAreaList.keys():
            for fullname in allPossibleBRFullnames:
                reExp, area = mainNamesRegexAreaList[mainName]
                matches = re.findall(reExp, fullname)
                if len(matches) > 0:
                    print("- " + mainName + " - nome encontrado na página. Sua área é: " + area)
                    break
    else:
        print("Status: url inválida - o website dado não possui assunto 'Lava Jato'")

    return 

if __name__ == "__main__":
	main()