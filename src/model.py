import torch
import torch.nn as nn


class ConcatEmbeddingsLayer(nn.Module):
    """ Layer that generates multiple embeddings and concats the result with the tensor.

    Parameters
    -------
    emb_columns : list<tuple>
        List of tuples where the first element is the name of the column,
        and the second is the distinct number of values of that column.

    Attributes
    -------
    embeddings: dict<nn.Embedding>
        Dict of embeddings where keys are the column names.
    dims : dict
        Dict where keys are column names and value is the dimension of
        the embedding.
    """
    def __init__(self, emb_columns):
        super().__init__()
        self.embeddings = {}
        self.emb_columns = emb_columns
        self.dims = {}

        for col, n_cat in emb_columns:
            dim = max(round(1.6 * n_cat**0.56), 3)  # TODO: Find paper (used params in fastAI)
            self.dims[col] = dim
            self.embeddings[col] = nn.Embedding(n_cat, dim)

    def forward(self, x, emb_data):
        embeddings = [self.embeddings[col[0]](emb_data[..., idx])
                      for idx, col in enumerate(self.emb_columns)]

        x = torch.cat((x, *embeddings), dim=1)

        return x

    @property
    def emb_dimension(self):
        """ Gets the total number of features obtained by concatenating every embedding.

        Returns
        -------
        dim : int
            Number of features of features obtained by concatenating every embedding.
        """
        return sum([val for _, val in self.dims.items()])


class DropoutDenseBNBlock(nn.Module):
    """ Dropout - Dense layer - Batch Normalization block.

    Parameters
    -------
    activation : function
        Activation function.
    p : float
        Probability of dropout.
    ni : int
        Number of input features.
    nh : int
        Number of hidden units.

    Attributes
    -------
    embeddings: dict<nn.Embedding>
        Dict of embeddings where keys are the column names.
    """

    def __init__(self, activation, p, ni, nh):
        super().__init__()
        self.dropout = nn.Dropout(p=p)
        self.linear = nn.Linear(in_features=ni, out_features=nh)
        self.activation = activation
        self.batchnorm = nn.BatchNorm1d(nh)

    def forward(self, x):
        x = self.dropout(x)
        x = self.linear(x)
        x = self.activation(x)
        x = self.batchnorm(x)

        return x


class SuperHeroNet(nn.Module):
    """ SuperHeroes network.

    Layer structure is:
    Embeddings - Dropout - Dense - BN - Dropout - Dense - BN - OutputLayer

    Parameters
    -------
    emb_columns : list<tuple>
        List of tuples where the first element is the name of the column,
        and the second is the distinct number of values of that column.
    n_input : int
        Number of input values that has not be embedded.
    n_classes : int
        Number of classes.
    p : list<float>
        Probablity of dropout for each layer.

    Attributes
    -------
    concatembeddings : ConcatenatedEmbeddingsLayer
        Layer that concatenates the float tensor with the embeddings of the
        different categorical features.
    block1 : DropoutDenseBNBlock
        First Dropout - Dense - Batch Norm block.
    block2 : DropoutDenseBNBlock
        Second Dropout - Dense - Batch Norm block.
    output : nn.Linear
        Last linear layer (without activation function).
    """
    def __init__(self, emb_columns, n_input, n_classes, p=[0.8, 0.5]):
        super().__init__()
        self.concatembeddings = ConcatEmbeddingsLayer(emb_columns)

        n = n_input + self.concatembeddings.emb_dimension
        nh1 = n // 50
        nh2 = nh1 // 4

        self.block1 = DropoutDenseBNBlock(nn.ReLU(), p[0], n, nh1)
        self.block2 = DropoutDenseBNBlock(nn.ReLU(), p[1], nh1, nh2)
        self.output = nn.Linear(in_features=nh2, out_features=n_classes)

    def forward(self, x, emb_data):
        x = self.concatembeddings(x, emb_data)
        x = self.block1(x)
        x = self.block2(x)
        x = self.output(x)

        return x
