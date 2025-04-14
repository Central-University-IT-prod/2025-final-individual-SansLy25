import json

from conf.settings import GIGACHAT_MODEL


def generate_ad_text(description, title, company_name):
    response = (
        GIGACHAT_MODEL.chat(
            "Сгенерируй рекламное объявление по описанию названию рекламы и компании,"
            " максимальная длина 400 символов, минимальная 120, ни в коем случае"
            " не пиши ничего кроме объявления это очень важно, НЕ ИСПОЛЬЗУЙ"
            " двойные кавычки, только одинарные, это тоже важно"
            " если описание абсолютно некорректное, например просто"
            " набор безсвязных символов или что то вообще не похожее на описание рекламы"
            " то в ответе напиши только слово 'Некорректно'\n"
            f"название компании: {company_name}\n"
            f"название рекламы: {title}\n"
            f"описание: {description}"
        )
        .choices[0]
        .message.content
    )

    return str(response).replace('"', ""), "некорректно" != response.lower()


def moderate(text):
    moderation_prompt = (
        "Тебе нужно модерировать текст рекламы. Ответ должен быть строго "
        'в формате: {"passed": true, "detail": "детально об ошибке"}. '
        "Очень важно ответить в точно таком же формате, ничего не добавляй. "
        'Поля: "passed" — флаг, пройдена модерация или нет; "detail" — '
        'подробно об ошибке. Если модерация пройдена успешно, "detail" '
        'принимает значение null. Вот статусы, которые могут быть в "detail":\n'
        '- "Violence and threats in the ad_text" — если в тексте есть насилие '
        "или угрозы\n"
        '- "Drugs and prohibited substances in the ad_text" — если в тексте '
        "есть что-то связанное с наркотиками\n"
        '- "Presence of obscene language in the ad_text" — если в тексте '
        "содержится нецензурная лексика\n"
        '- "Direct insults to specific groups or individuals in the ad_text" — '
        "если в тексте есть расизм, нацизм, оскорбления конкретных лиц или "
        "групп\n"
        '- "Absolutely unreadable ad_text" — если текст представляет собой '
        "набор несвязных символов или слов, никак не связанных по смыслу\n"
        "Твой ответ должен быть однозначным. Если текст подходит под несколько "
        f"пунктов, выбирай любой. Вот текст: {text}"
    )

    response = GIGACHAT_MODEL.chat(moderation_prompt).choices[0].message.content

    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        response = {
            "passed": False,
            "detail": "LLM could not interpret your ad_text, it is incorrect",
        }

    return response
