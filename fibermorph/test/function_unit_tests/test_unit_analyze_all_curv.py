import pathlib
import skimage

import numpy as np
from skimage import measure
import pandas as pd
from skimage import io

from fibermorph.test.function_unit_tests.test_unit_analyze_each_curv import analyze_each_curv
from fibermorph.test.function_unit_tests.test_unit_check_bin import check_bin

# analyzes curvature for entire image (analyze_each does each hair in image)

def analyze_all_curv(img, name, analysis_dir, resolution, window_size_mm=1):

    if type(img) != 'numpy.ndarray':
        print(type)
        img = np.array(img)
    else:
        print(type(img))

    print("Analyzing {}".format(name))
    
    img = check_bin(img)

    label_image, num_elements = skimage.measure.label(img.astype(int), connectivity=2, return_num=True)
    print("\n There are {} elements in the image".format(num_elements))

    props = skimage.measure.regionprops(label_image)

    window_size = int(round(window_size_mm * resolution))  # must be an integer
    print("\nWindow size for analysis is {} pixels".format(window_size))
    print("Analysis of curvature for each element begins...")
    tempdf = [analyze_each_curv(hair, window_size, resolution) for hair in props]

    print("\nData for {} is:".format(name))
    print(tempdf)

    within_curvdf = pd.DataFrame(tempdf, columns=['curv_mean', 'curv_median', 'length'])

    print("\nDataframe for {} is:".format(name))
    print(within_curvdf)
    print(within_curvdf.dtypes)

    # remove outliers
    q1 = within_curvdf.quantile(0.1)
    q3 = within_curvdf.quantile(0.9)
    iqr = q3 - q1

    within_curv_outliers = within_curvdf[~((within_curvdf < (q1 - 1.5 * iqr)) | (within_curvdf > (q3 + 1.5 * iqr))).any(axis=1)]

    print(within_curv_outliers)

    within_curvdf2 = pd.DataFrame(within_curv_outliers, columns=['curv_mean', 'curv_median', 'length']).dropna()
    
    print("\nDataFrame with NaN values dropped:")
    print(within_curvdf2)
    
    with pathlib.Path(analysis_dir).joinpath(name + ".csv") as save_path:
        within_curvdf2.to_csv(save_path)

    curv_mean_im_mean = within_curvdf2['curv_mean'].mean()
    curv_mean_im_median = within_curvdf2['curv_mean'].median()
    curv_median_im_mean = within_curvdf2['curv_median'].mean()
    curv_median_im_median = within_curvdf2['curv_median'].median()
    length_mean = within_curvdf2['length'].mean()
    length_median = within_curvdf2['length'].median()
    hair_count = len(within_curvdf2.index)

    sorted_df = pd.DataFrame(
        [name, curv_mean_im_mean, curv_mean_im_median, curv_median_im_mean, curv_median_im_median, length_mean,
         length_median, hair_count]).T

    print("\nDataframe for {} is:".format(name))
    print(sorted_df)
    print("\n")

    return sorted_df

input_file = skimage.io.imread("/Users/tinalasisi/Desktop/2019_05_17_fibermorphTestImages/pruned_curv.tiff", as_gray=True)

output_path = "/Users/tinalasisi/Desktop/2019_05_17_fibermorphTestImages"

sorted_df = analyze_all_curv(input_file, "testcase", output_path, resolution=132, window_size_mm=1)