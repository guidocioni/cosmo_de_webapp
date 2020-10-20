from utils import *


f_steps = list(range(0, 28))


date_string, _ = get_run()
urls = find_file_name(vars_2d=None,
                      vars_3d=['t@850', 'fi@500'],
                      f_times=f_steps)

fils = download_extract_files(urls)