import numpy as np
import torch.nn as nn
import torch

from fastai.layers import BaseLoss


class BPRLoss(nn.modules.loss._Loss):
    """ BPRLoss for non matrix factorization at input.

    Parameters
    -------
    neg_sample : int
        Number of negative classes that are selected per positive class.
    """
    def __init__(self, neg_sample=3):
        super().__init__()
        self.neg_sample = neg_sample

    def forward(self, output, target):
        bs = output.size()[0]
        c = output.size()[-1]

        loss = 0
        n = 0
        for i in range(bs):
            neg = (target[i] == 0).nonzero().squeeze().numpy()
            pos = target[i].nonzero().numpy()
            size = min(c - len(pos), self.neg_sample)
            for pos_idx in pos:
                neg_idx = np.random.choice(neg, size, replace=False)

                n += len(neg_idx)
                loss -= (output[i, pos_idx] - output[i, neg_idx]).sigmoid().log().sum()

        return loss / n

    def activation(self, out):
        return torch.sigmoid(out)

    def decodes(self, out):
        return out > 0.5


class BPRLossFlat(BaseLoss):
    """"Same as `BPRLoss` but for fastAI.
    """
    def __init__(self, *args, axis=-1, **kwargs):
        super().__init__(BPRLoss, *args, axis=axis, is_2d=True, flatten=False,  **kwargs)

    def activation(self, out):
        return torch.sigmoid(out)

    def decodes(self, out):
        return out > 0.5
