"""
Neccessory Module imports
"""
import argparse
import json
import math
import multiprocessing
from service import service_func


def main(arguments):
    """
    Funcrion Description
    """

    wb_list = json.loads(arguments.project_data)
    num_proc = multiprocessing.cpu_count()
    workbook_iteration = math.ceil(len(wb_list) / num_proc)
    iter_split_start, iter_split_end, jobs = 0, num_proc, []
    mp_manager = multiprocessing.Manager()
    mpd = mp_manager.list()

    for data in wb_list:
        mpd.append(mp_manager.dict(
            {'wb_name': data['publish_wb_data']['wb_name'],
             '_is_' + data['publish_wb_data']['wb_name'] + '_published': None,
             '_is_' + data['publish_wb_data']['wb_name'] + '_permissions_updated': None,
             '_is_' + data['publish_wb_data']['wb_name'] + '_datasource_updated': None}))

    for _ in range(int(workbook_iteration)):
        for workbook in wb_list[iter_split_start:iter_split_end]:
            process = multiprocessing.Process(
                target=service_func,
                args=(workbook, arguments.username, arguments.password,
                      arguments.produsername, arguments.prodpassword, mpd))
            jobs.append(process)

        for job in jobs:
            job.start()

        for job in jobs:
            job.join()

        iter_split_start += num_proc
        iter_split_end += num_proc
        jobs = []

        for i in mpd:
            for key, val in i.items():
                print(f"{key}: {val}")
                # if val == False:
                #     exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument('--username', action='store',
                        type=str, required=True)
    parser.add_argument('--password', action='store',
                        type=str, required=True)
    parser.add_argument('--produsername', action='store',
                        type=str, required=True)
    parser.add_argument('--prodpassword', action='store',
                        type=str, required=True)
    parser.add_argument('--project_data', action='store',
                        type=str, required=True)
    args = parser.parse_args()
    main(args)
