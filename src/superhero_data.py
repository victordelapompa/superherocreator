import pickle

from tqdm import tqdm
import torch
from torch.utils.data import Dataset


from preprocessing import get_bert, text2embedding


class SuperHeroDataset(Dataset):
    STRING_COLS = ['affiliation', 'occupation', 'citizenship', 'eyes', 'origin', 'hair']
    EMBEDDING_COLS = ['gender_num', 'identity_num', 'universe_num']
    TARGET_COL = 'powers_idx'
    """ Dataset class for superheroes.

    Parameters
    -------
    df : pandas.DataFrame
        DataFrame with data.
    model_name : str
        Bert model used.
    init_string : str
        If not none first element of the text ([CLS] in BERT).
    end_string : str
        If not none last element of the text ([SEP] in BERT).
    idx : int
        Index of the token that is going to be fed to later layers.
    n_classes : int
        Number of classes.
    folder : str
        If not None pickles every row in the folder.

    Attributes
    -------
    tokenizer : BertTokenizer
        Bert tokenizer from transformer lib. (PyTorch).
    model : BertModel
        Bert model from transformer lib. (PyTorch).
    """

    def __init__(self, df, model_name, init_string, end_string, idx, n_classes, folder=None):
        self.df = df
        self.tokenizer, self.model = get_bert(name=model_name)
        self.init_string = init_string
        self.end_string = end_string
        self.idx = idx
        self.n_classes = n_classes

        if folder is not None:
            self.folder = folder
            self._pickle_all()
            self._getitem = self._load_index
        else:
            self._getitem = self._get_val_idx

    def __len__(self):
        return self.df.shape[0]

    def __getitem__(self, index):
        return self._getitem(index)

    def _get_val(self, row):
        """ Gets the x value for a row (dictionary or pandas.Series).

        Parameters
        -------
        row : pandas.Series
            Anytype of object that has a __getitem__ and works with strings.

        Returns
        -------
        data_val : torch.tensor
            Concatenated embedding values for one token.
        embedding_data : torch.tensor
            Categorical data that has to be embbeded first.
        """
        with torch.no_grad():
            arr = [self.text2embedding_idx(row[col])
                   for col in SuperHeroDataset.STRING_COLS]

        embedding_data = torch.tensor(row[SuperHeroDataset.EMBEDDING_COLS]).long()

        data_val = torch.cat(arr)

        return data_val, embedding_data

    def _get_val_idx(self, index):
        """ Gets the x and y value for a index.

        Parameters
        -------
        index : int
            Index.

        Returns
        -------
        data_val : torch.tensor
            Concatenated embedding values for one token.
        embedding_data : torch.tensor
            Categorical data that has to be embbeded first.
        target : int
            Value of target.
        """

        row = self.df.iloc[index]
        data_val, embedding_data = self._get_val(row)

        # One hot target and sum over all the powers
        t = torch.tensor(row[SuperHeroDataset.TARGET_COL])
        target = torch.nn.functional.one_hot(t, num_classes=self.n_classes).sum(axis=0)

        return data_val, embedding_data, target

    def _pickle_all(self):
        n = len(self)

        for i in tqdm(range(n)):
            res = self._get_val_idx(i)
            path = self.folder + str(i)
            with open(path, 'wb') as file:
                pickle.dump(res, file)

    def _load_index(self, index):
        path = self.folder + str(index)
        with open(path, 'rb') as file:
            data_val, embedding_data, target = pickle.load(file)

        return data_val, embedding_data, target

    def text2embedding_idx(self, text):
        """ Gets the embedding value for one token in a text with a pretrained model.

        Parameters
        -------
        text : str
            String with the text to be transformed.

        Returns
        -------
        torch.tensor
            Embedding values for one token.
        """
        emb = text2embedding(text, self.tokenizer, self.model, self.init_string, self.end_string)

        return emb[self.idx]
