import pickle

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import torch

from constants import (PUBLIC_IDENTITY, SECRET_IDENTITY, NO_DUAL_IDENTITY,
                       KNOWN_AUTHORITIES_IDENTITY, UNKNOWN_IDENTITY,
                       MALE_GENDER, FEMALE_GENDER, AGENDER_GENDER, UNKNOWN_GENDER)


def main():
    data_path = '../data/data.pkl'
    train_path = '../data/train/v1/data.pkl'
    model_path = '../models/model.pkl'

    # Load data
    result, train = load_data(path=data_path, train_path=train_path)

    idx2power = result['idx2power']
    universe2idx = dict(result['universe2idx'])
    df = result['data']

    gender2idx = get_gender_dict()
    identity2idx = get_identity_dict()

    # Load model
    model = load_model(model_path)

    st.sidebar.markdown('Information about you')

    universe = frame_selectbox_ui('What is your universe?', list(universe2idx.keys()))
    identity = frame_selectbox_ui('What is your identity?', list(identity2idx.keys()))
    gender = frame_selectbox_ui('What is your gender?', list(gender2idx.keys()))

    data = {'gender_num': gender2idx[gender],
            'identity_num': identity2idx[identity],
            'universe_num': universe2idx[universe]}

    for col in train.STRING_COLS:
        data[col] = st.sidebar.text_input(col.capitalize(), value='')

    n_powers = st.number_input('How many powers do you have?', 1, 40, 2)

    y_score = get_scores(model, train, data)
    idx_powers, scores = get_powers(y_score, n_powers)

    df_close_sh = get_close_heroes(idx_powers, df)


    st.write('The following heroes have similar powers:')
    st.dataframe(df_close_sh)

    powers = [idx2power[idx] for idx in idx_powers]

    fig, ax = plt.subplots(figsize=(5, n_powers * 1))
    ax.barh(powers, scores)
    ax.invert_yaxis()

    st.pyplot(fig)


def frame_selectbox_ui(box_text, arr):
    selection = st.sidebar.selectbox(box_text, sorted(arr), 0)

    return selection


def load_data(path, train_path):
    """ Loads data from path.

    Parameters
    -------
    path : string
        Path where the data is stored with a pickle.
    train_path : string
        Path where the training dataset was stored.

    Returns
    -------
    result : dict
        A trained pytorch network.
    train : SuperHeroDataset
        Dataset used in training.
    """
    with open(path, 'rb') as f:
        result = pickle.load(f)

    with open(train_path, 'rb') as f:
        train = pickle.load(f)

    return result, train


def load_model(path):
    """ Loads model from path.

    Parameters
    -------
    path : string
        Path where the model is stored with a pickle.

    Returns
    -------
    model : torch.nn.Module
        A trained pytorch network.
    """
    with open(path, 'rb') as f:
        model = pickle.load(f)

    return model


@st.cache
def get_scores(model, train, data):
    """ Gets the scoring value for each superpower.

    Parameters
    -------
    model : torch.nn.Module
        A trained pytorch network.
    train : SuperHeroDataset
        Dataset used in training.
    row : pandas.Series
        Anytype of object that has a __getitem__ and works with strings.

    Returns
    -------
    y_score : torch.tensor
        Scoring for each class.
    """
    x, emb_data = train._get_val(pd.Series(data))

    with torch.no_grad():
        y_score = model.forward(x.unsqueeze(0), emb_data.unsqueeze(0))

    return y_score.squeeze()


def get_powers(y_score, n_powers):
    """ Gets the n_powers with higher score.

    Parameters
    -------
    y_score : torch.tensor
        Scoring for each class.
    n_powers : int
        Number of powers.

    Returns
    -------
    powers : list<int>
        List of powers as index.
    scores: list<float>
        List of scores for each power.
    """
    y_pred_scores, y_pred = torch.topk(y_score, k=n_powers, largest=True, sorted=True)

    powers = y_pred.tolist()
    scores = torch.sigmoid(y_pred_scores).tolist()

    return powers, scores


def get_close_heroes(powers, df, show_cols=['name', 'alias'], k=3):
    """ Calculates similarity between the list of powers by using jaccard distance.

    Parameters
    -------
    powers : list<int>
        List of powers.
    df : pd.DataFrame
        DataFrame with all the data.
    show_cols : list<str>
        List of columns to show.
    k : int
        Number of neighbours by powers.

    Returns
    -------
    df_res : pd.DataFrame
        DataFrame with the top k similar super heroes.
    """
    def jaccard(x, y):
        x = set(x)
        y = set(y)

        return len(x.intersection(y)) / len(x.union(y))

    df = df.copy()
    df['similarity'] = df['powers_idx'].apply(lambda x: jaccard(x, powers))

    df_res = df.fillna(0).sort_values(by='similarity', ascending=False)

    return df_res[show_cols].iloc[:k]


def get_gender_dict():
    gender2idx = {'Male': MALE_GENDER,
                  'Female': FEMALE_GENDER,
                  'Agender': AGENDER_GENDER,
                  'UNKNOWN': UNKNOWN_GENDER}

    return gender2idx


def get_identity_dict():
    identity2idx = {'Public': PUBLIC_IDENTITY,
                    'Secret': SECRET_IDENTITY,
                    'No dual': NO_DUAL_IDENTITY,
                    'Unknown': UNKNOWN_IDENTITY,
                    'Known by authorities': KNOWN_AUTHORITIES_IDENTITY}

    return identity2idx


if __name__ == "__main__":
    main()
