import os
from os.path import join
from pathlib import Path
import numpy as np
import nibabel as nib
import pandas as pd

import torch
from torch.utils.data import Dataset

class SliceDataset(Dataset):
    def __init__(self, im_ids: np.array,
                 pos_slice_dict: dict,
                 transforms=None,
                 preprocessing=None,
                 p_pos_per_sample: float = 0.33):
        """
        Reads from a directory of 2D slice numpy arrays and samples positive
        slices. Assumes the data directory contains 2D slices processed by
        `io.Preprocessor.save_dir_as_2d()`.
        Attributes
            im_ids (np.ndarray): of image names.
            pos_slice_dict (dict or pd.DataFrame): dictionary generated by
                `io.Preprocessor.save_dir_as_2d()`
            transforms (albumentations.augmentation): transforms to apply
                before preprocessing. Defaults to HFlip and ToTensor
            preprocessing: ops to perform after transforms, such as
                z-score standardization. Defaults to None.
            p_pos_per_sample (float): probability at which to sample slices
                that contain foreground classes.
        """
        self.im_ids = im_ids
        self.pos_slice_dict = pos_slice_dict
        self.transforms = transforms
        self.preprocessing = preprocessing
        self.p_pos_per_sample = p_pos_per_sample
        print(f"Assuming inputs are .npy files...")
        self.check_fg_idx_per_class()

    def __getitem__(self, idx):
        # loads data as a numpy arr and then adds the channel + batch size dimensions
        case_id = self.im_ids[idx]
        x, y = self.load_slices(case_id)
        if self.transforms:
            # adds the batch size dim if needed
            x = x[None] if len(x.shape) == 3 else x
            y = y[None] if len(y.shape) == 3 else y
            # batchgenerators requires shape: (b, c, ...)
            data_dict = self.transforms(**{"data": x, "seg": y})
            x, y = data_dict["data"], data_dict["seg"]
        if self.preprocessing:
            preprocessed = self.preprocessing(**{"data": x, "seg": y})
            x, y = preprocessed["data"], preprocessed["seg"]
        # squeeze to remove batch size dim
        x = torch.squeeze(x, dim=0).float()
        y = torch.squeeze(y, dim=0)
        return (x, y)

    def __len__(self):
        return len(self.im_ids)

    def load_slices(self, case_fpath):
        """
        Gets the slice idx using self.get_slice_idx_str() and actually loads
        the appropriate slice array.
        """
        slice_idx_str = self.get_slice_idx_str(case_fpath)
        x_path = join(case_fpath, f"imaging_{slice_idx_str}.npy")
        y_path = join(case_fpath, f"segmentation_{slice_idx_str}.npy")
        return (np.load(x_path)[None], np.load(y_path)[None])

    def get_slice_idx_str(self, case_fpath):
        """
        Gets the slice idx and processes it so that it fits how the arrays
        were saved by `io.Preprocessor.save_dir_as_2d`.
        """
        # extracting slice:
        temp_p = np.random.uniform(0, 1)
        if temp_p < self.p_pos_per_sample:
            slice_idx = self.get_rand_pos_slice_idx(case_fpath)
        else:
            slice_idx = self.get_rand_slice_idx(case_fpath)
        # formatting string
        slice_idx_str = str(slice_idx)
        while len(slice_idx_str) < 3:
            slice_idx_str = "0"+slice_idx_str
        return slice_idx_str

    def get_rand_pos_slice_idx(self, case_fpath):
        """
        Gets a random positive slice index from self.pos_slice_dict (that was generated by
        io.preprocess.Preprocessor when save_as_slices=True).
        Args:
            case_fpath: each element of self.im_ids (path to a case folder)
        Returns:
            an integer representing a random non-background class slice index
        """
        case_raw = Path(case_fpath).name
        # finding random positive class index
        if self.fg_idx_per_class:
            sampled_class = np.random.choice(self.fg_classes)
            slice_indices = self.pos_slice_dict[case_raw][sampled_class]
            random_pos_coord = np.random.choice(slice_indices)
        else:
            random_pos_coord = np.random.choice(self.pos_slice_dict[case_raw])
        return random_pos_coord

    def get_rand_slice_idx(self, case_fpath):
        """
        Args:
            case_fpath: each element of self.im_ids (path to a case folder)
        Returns:
            A randomly selected slice index
        """
        # assumes that there are no other files in said directory with "imaging_"
        _slice_files = [file for file in os.listdir(case_fpath)
                        if file.startswith("imaging_")]
        return np.random.randint(0, len(_slice_files))

    def check_fg_idx_per_class(self):
        """
        checks the first key: value pair of self.pos_slice_dict
        If dict -> fg_idx_per_class, if list: not fg_idx_per_class
        fg_idx_per_class -> uniformly sample per class v. sample all fg idx
        """
        dummy_key = list(self.pos_slice_dict.keys())[0]
        dummy_value = self.pos_slice_dict[dummy_key]
        self.fg_idx_per_class = True if isinstance(dummy_value, dict) else False
        if self.fg_idx_per_class:
            self.fg_classes = list(dummy_value.keys())
