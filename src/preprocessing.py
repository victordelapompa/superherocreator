import torch
from transformers import BertTokenizer, BertModel


def get_bert(name='bert-base-uncased'):
    """ Gets BertTokenizer and Model.

    Parameters
    -------
    name : str
        Bert version.

    Returns
    -------
    tokenizer : transformers.BertTokenizer
    model : transformers.BertModel
    """
    tokenizer = BertTokenizer.from_pretrained(name)
    model = BertModel.from_pretrained(name)
    return tokenizer, model


def text2embedding(text, tokenizer, model, init_string='', end_string=''):
    """ Gets the embedding value for each token in a text with a pretrained model.

    Parameters
    -------
    text : str
        String with the text to be transformed.
    tokenizer:
        Tokenizer from transformer library.
    model :
        Model from transformer library.
    init_string :
        If not none first element of the text ([CLS] in BERT).
    end_string :
        If not none last element of the text ([SEP] in BERT).

    Returns
    -------
    torch.tensor
        Embedding values for all the text
    """
    if init_string != '' or end_string != '':
        if text is None or text == '':
            text = init_string + ' ' + end_string
        else:
            text = (init_string + ' ' + text + ' ' + end_string).strip()

    input_ids = torch.tensor(tokenizer.encode(text)).unsqueeze(0)
    outputs = model(input_ids)
    text_embedded = outputs[0]

    return text_embedded.squeeze()


def strings2embedding(arr_str, tokenizer, model):
    """ Gets the embedding value for each element of a list with a pretrained model.

    Note that this version forces that every elemnent of the array
    should have the same number of words.

    Parameters
    -------
    arr_str : list<str>
        List of strings to be transformed
    tokenizer:
        Tokenizer from transformer library.
    model :
        Model from transformer library.

    Returns
    -------
    torch.tensor
        Embedding value for each string
    """
    input_ids = torch.tensor(tokenizer.encode([string for string in arr_str]))
    if len(input_ids.shape) == 1:
        input_ids = input_ids.unsqueeze(0)

    outputs = model(input_ids)
    text_embedded = outputs[0]

    return text_embedded
