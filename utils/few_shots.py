HEB_FEW_SHOT_FOR_VERB_QUESTIONS = """
what became something? | התבררה
מה התברר למשהו?

when did someone discuss something? | דנה
מתי מישהו דן על משהו?

who would formulate something? | תגבש
מי יגבש משהו?

who did someone shriek at? | צווח
על מי מישהו צווח?

who established something? | הקים
מי הקים משהו?

what has made something? | הבהיר
מה הבהיר משהו?

what would something regulate? | תסדיר
מה משהו יסדיר?

what would regulate something? | תסדיר
מה יסדיר משהו?

what is something based on? | מבוססת
על מה משהו מבוסס?

"""

RU_FEW_SHOT_FOR_VERB_QUESTIONS = """
what became something? | Оказалось
Что оказалось чем-то?

when did someone discuss something? | обсуждала
когда кто-то обсуждал что-то?

what did someone build? | построивших
что кто-то построил?

who did someone shriek at? | кричал
на кого кто-то кричал?

who was killed? | погибших
кто погиб?

where is something wintering? | зимуют
где что-то зимует?

what would something regulate? | регулировать
что что-то будет регулировать?

what would regulate something? | регулировать
что будет регулировать что-то?

what is something based on? | основана
на чем что-то основано?

"""


HEB_FEW_SHOT_FOR_VERB_PREDICATE_DECISION = '''
'organizer' | ['מארגנת', 'קהילתית']
מארגנת

shrieked | ['צווח', 'עיתונאים']
צווח

cancellation | ['תביעה', 'לבטל', 'הזמנה_']
לבטל

extradited | ['שלטונות', 'יוסגר']
יוסגר

provoked | ['עורר', 'יריב']
עורר

'''

RU_FEW_SHOT_FOR_VERB_PREDICATE_DECISION = '''
'organizer' | ['организатор', 'общественный']
организатор

shrieked | ['журналисты', 'кричал']
кричал

cancellation | ['отменить', 'приглашение']
отменить

freed | ['погибших', 'освобождения']
освобождения

spent | ['его', 'прошла']
прошла

'''

HEB_FEW_SHOT_FOR_NOM_PREDICATE_DECISION = '''
'transfusion' | ['עירוי', 'פלזמה']
עירוי

'infections' | ['תגובות', 'זיהומים']
זיהומים

clotting | ['חלבונים', 'קרישה']
קרישה

bleeding | ['דימום', 'טראומה']
דימום

indications | ['כוללות', 'אינדיקציות']
אינדיקציות

'''

RU_FEW_SHOT_FOR_NOM_PREDICATE_DECISION = '''
'transfusion' | ['переливание', 'плазма']
переливание

'infections' | ['реакции', 'инфекции']
инфекции

clotting | ['белки', 'свертывание']
свертывание

bleeding | ['кровотечение', 'травма']
кровотечение

indications | ['включают', 'индикации']
индикации

'''

HEB_FEW_SHOT_FOR_NOMINALIZATION_PREDICTION = """
הקטלה: שם פעולה
שולחן : שם עצם 
צלחת : שם עצם
הזמנה : שם פעולה
מתן : שם פעולה
היתר : שם פעולה
וועדה : שם עצם
איסור : שם פעולה
שמיעה : שם פעולה
אוזן : שם עצם
היטל : שם פעולה
גשם : שם עצם
ממשלה : שם עצם
"""

RU_FEW_SHOT_FOR_NOMINALIZATION_PREDICTION = """
убийство: имя действия
стол : имя существительное
тарелка : имя существительное
приглашение : имя действия
дарение : имя действия
разрешение : имя действия
комитет : имя существительное
запрещение : имя действия
слух : имя действия
ухо : имя существительное
освобождение : имя действия
дождь : имя существительное
правительство : имя существительное
"""

HEB_FEW_SHOT_FOR_NOM_CONSTRAIN_TRANSLATION = """
what is defined? | הגדרה
מה מוגדר?
    
what might someone feel? | תחושת
מה עלול מישהו לחוש?

when is something transfused? | עירויי
מתי מישהו עובר עירוי דם?

where is something excepted? | למעט
איפה משהו התמעט?

when wasn't someone infected? | זיהום
מתי מישהו לא זוהם?

"""

RU_FEW_SHOT_FOR_NOM_CONSTRAIN_TRANSLATION = """
what is defined? | определение
что определено?

what might someone feel? | чувство
что кто-то может почувствовать?

when is something transfused? | переливание
когда что-то переливается?

where did someone support something? | поддержка
где кто-то поддержал что-то?

when wasn't something decided? | решение
когда что-то не было решено?

"""

HE_FEW_SHOT_FOR_PREDICATE_DECISION = '''
organizer | ['מארגן', 'קהילתי']
מארגן

shrieked | ['צווח', 'עיתונאי']
צווח

infections | ['תגובות', 'זיהומים']
זיהומים

extradited | ['שלטונות', 'יוסגר']
יוסגר

bleeding | ['דימום', 'טראומה']
דימום

argued | ['התווכח', 'עמדה']
התווכח

expulsion | ['גרוש', 'תלמיד']
גורש

negotiation | ['ניהל', 'משא']
ניהל

observed | ['צפה', 'כוכב']
צפה

recession | ['מיתון', 'שגשוג']
מיתון

emphasize | ['ב', 'להדגיש', 'נקלענו']
להדגיש

'''

RU_FEW_SHOT_FOR_PREDICATE_DECISION = '''
organizer | ['организатор', 'общественный']
организатор

shrieked | ['журналисты', 'кричал']
кричал

infections | ['реакции', 'инфекции']
инфекции

freed | ['погибших', 'освобождения']
освобождения

spent | ['его', 'прошла']
прошла

'''


FR_FEW_SHOT_FOR_VERB_QUESTIONS = """
what became something? | est devenu
qu'est-ce qui est devenu quelque chose?

when did someone discuss something? | discuté
quand quelqu'un a-t-il discuté de quelque chose?

who would formulate something? | formulerait
qui formulerait quelque chose?

who did someone shriek at? | crié
sur qui quelqu'un a-t-il crié?

who established something? | établi
qui a établi quelque chose?

what has made something? | a fait
qu'est-ce qui a fait quelque chose?

what would something regulate? | régulerait
qu'est-ce que quelque chose régulerait-il?

what would regulate something? | régulerait
qu'est-ce qui régulerait quelque chose?

what is something based on? | basée
sur quoi quelque chose est-il basé?

"""


FR_FEW_SHOT_FOR_NOMINALIZATION_PREDICTION = """
meurtre: nom d'action
table : nom commun
assiette : nom commun
invitation : nom d'action
don : nom d'action
permission : nom d'action
comité : nom commun
interdiction : nom d'action
audition : nom d'action
oreille : nom commun
libération : nom d'action
pluie : nom commun
gouvernement : nom commun
"""


FR_FEW_SHOT_FOR_NOM_CONSTRAIN_TRANSLATION = """
what is defined? | définition
qu'est-ce qui est défini?

what might someone feel? | sentiment
qu'est-ce que quelqu'un pourrait ressentir?

when is something transfused? | transfusion
quand quelque chose est-il transfusé?

where is something excepted? | sauf
où quelque chose est-il excepté?

when wasn't someone infected? | infection
quand quelqu'un n'était-il pas infecté?

"""


FR_FEW_SHOT_FOR_PREDICATE_DECISION = '''
organizer | ['organisateur', 'communautaire']
organisateur

shrieked | ['crié', 'journaliste']
crié

infections | ['réactions', 'infections']
infections

extradited | ['autorités', 'extradié']
extradié

bleeding | ['saignement', 'traumatisme']
saignement

argued | ['disputé', 'position']
disputé

expulsion | ['expulsion', 'étudiant']
expulsion

observed | ['regardé', 'étoile']
regardé

'''
