#!/usr/bin/python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import json
import logging
import os
import random

import numpy as np
import torch
from torch.utils.data import DataLoader
from kgreasoning.models import KGReasoning
from kgreasoning.dataloader import TestDataset, TrainDataset, TrainOtherDataset, SingledirectionalOneShotIterator
from tensorboardX import SummaryWriter
import time
import pickle
from collections import defaultdict
from tqdm import tqdm
from kgreasoning.util import flatten_query, list2tuple, parse_time, set_global_seed, eval_tuple
"""
query_name_dict = {('e',('r',)): '1p', 
                    ('e', ('r', 'r')): '2p',
                    ('e', ('r', 'r', 'r')): '3p',
                    ('e', ('r', 'r', 'r', 'r')): '4p',
                    ('e', ('r', 'r', 'r', 'r', 'r')): '5p',
                    #(('e', ('r',)), ('e', ('r',))): '2i',
                    #(('e', ('r',)), ('e', ('r',)), ('e', ('r',))): '3i',
                    (('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r'))): '2i',
                    (('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r'))): '3i',
                    (('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r'))): '4i',
                    (('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r'))): '5i',
                    (('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r'))): '6i',
                   (('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r'))): '7i',
                   (('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r'))): '8i',
                   (('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r'))): '9i',
                   (('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r'))): '10i',
                   (('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r'))): '11i',
                   (('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r'))): '12i',
                   (('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r'))): '13i',
                   (('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r'))): '14i',
                   (('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r'))): '15i',
                   (('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r'))): '16i',
                   (('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r'))): '17i',
                   (('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r'))): '18i',
                   (('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r'))): '19i',
                   (('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r'))): '20i',
                   (('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r'))): '21i',
                   (('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r'))): '22i',
                   (('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r'))): '23i',
                   (('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r'))): '24i',
                   (('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r'))): '25i',
                   (('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r')), ('e', ('r', 'r', 'r'))): '26i',
                    ((('e', ('r',)), ('e', ('r',))), ('r',)): 'ip',
                    (('e', ('r', 'r')), ('e', ('r',))): 'pi',
                    (('e', ('r',)), ('e', ('r', 'n'))): '2in',
                    (('e', ('r',)), ('e', ('r',)), ('e', ('r', 'n'))): '3in',
                    ((('e', ('r',)), ('e', ('r', 'n'))), ('r',)): 'inp',
                    (('e', ('r', 'r')), ('e', ('r', 'n'))): 'pin',
                    (('e', ('r', 'r', 'n')), ('e', ('r',))): 'pni',
                    (('e', ('r',)), ('e', ('r',)), ('u',)): '2u-DNF',
                    ((('e', ('r',)), ('e', ('r',)), ('u',)), ('r',)): 'up-DNF',
                    ((('e', ('r', 'n')), ('e', ('r', 'n'))), ('n',)): '2u-DM',
                    ((('e', ('r', 'n')), ('e', ('r', 'n'))), ('n', 'r')): 'up-DM'
                }
name_query_dict = {value: key for key, value in query_name_dict.items()}
all_tasks = list(name_query_dict.keys()) # ['1p', '2p', '3p', '4p', '5p', '2i', '3i', '4i', 5i', 'ip', 'pi', '2in', '3in', 'inp', 'pin', 'pni', '2u-DNF', '2u-DM', 'up-DNF', 'up-DM']
"""
query_name_dict = {('e',('r',)): '1p', 
                    ('e', ('r', 'r')): '2p',
                    ('e', ('r', 'r', 'r')): '3p',
                    ('e', ('r', 'r', 'r', 'r')): '4p',
                    ('e', ('r', 'r', 'r', 'r', 'r')): '5p'
                  }
total_intr = 110
for num_intr in range(2,total_intr+1):
    query_structure = []
    for _ in range(num_intr):
        query_structure.append(('e', ('r', 'r', 'r')))
    query_name_dict[tuple(query_structure)] = str(num_intr)+'i'
name_query_dict = {value: key for key, value in query_name_dict.items()}
all_tasks = list(name_query_dict.keys()) # ['1p', '2p', '3p', '4p', '5p', '2i', '3i', '4i', 5i', 'ip', 'pi', '2in', '3in', 'inp', 'pin', 'pni', '2u-DNF', '2u-DM', 'up-DNF', 'up-DM']

def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description='Training and Testing Knowledge Graph Embedding Models',
        usage='train.py [<args>] [-h | --help]'
    )

    parser.add_argument('--cuda', action='store_true', help='use GPU')
    
    parser.add_argument('--do_train', action='store_true', help="do train")
    parser.add_argument('--do_valid', action='store_true', help="do valid")
    parser.add_argument('--do_test', action='store_true', help="do test")

    parser.add_argument('--data_path', type=str, default=None, help="KG data path")
    parser.add_argument('-n', '--negative_sample_size', default=128, type=int, help="negative entities sampled per query")
    parser.add_argument('-d', '--hidden_dim', default=500, type=int, help="embedding dimension")
    parser.add_argument('-g', '--gamma', default=12.0, type=float, help="margin in the loss")
    parser.add_argument('-b', '--batch_size', default=1024, type=int, help="batch size of queries")
    parser.add_argument('--test_batch_size', default=1, type=int, help='valid/test batch size')
    parser.add_argument('-lr', '--learning_rate', default=0.0001, type=float)
    parser.add_argument('-cpu', '--cpu_num', default=10, type=int, help="used to speed up torch.dataloader")
    parser.add_argument('-save', '--save_path', default=None, type=str, help="no need to set manually, will configure automatically")
    parser.add_argument('--max_steps', default=100000, type=int, help="maximum iterations to train")
    parser.add_argument('--warm_up_steps', default=None, type=int, help="no need to set manually, will configure automatically")
    
    parser.add_argument('--save_checkpoint_steps', default=50000, type=int, help="save checkpoints every xx steps")
    parser.add_argument('--valid_steps', default=10000, type=int, help="evaluate validation queries every xx steps")
    parser.add_argument('--log_steps', default=100, type=int, help='train log every xx steps')
    parser.add_argument('--test_log_steps', default=1000, type=int, help='valid/test log every xx steps')
    
    parser.add_argument('--use_pretrain', default=0, type=int, help="use pretrained user and item embeddings. Only for BetaE") # pretrain 
    parser.add_argument('--pretrain_embedding_dir', nargs='?', default='data/pretrain/',help='Path of learned embeddings. No need to set manually, will configure automatically')
    
    parser.add_argument('--nentity', type=int, default=0, help='DO NOT MANUALLY SET')
    parser.add_argument('--nrelation', type=int, default=0, help='DO NOT MANUALLY SET')
    parser.add_argument('--nitems', type=int, default=0, help='DO NOT MANUALLY SET')
    parser.add_argument('--start_item', type=int, default=0, help='DO NOT MANUALLY SET')
    
    parser.add_argument('--geo', default='beta', type=str, choices=['vec', 'box', 'beta'], help='the reasoning model, vec for GQE, box for Query2box, beta for BetaE')
    parser.add_argument('--print_on_screen', action='store_true')
    
    parser.add_argument('--tasks', default='1p.2p.3p.4p.5p.2i.3i.4i.5i.ip.pi.2in.3in.inp.pin.pni.2u.up', type=str, help="tasks connected by dot, refer to the BetaE paper for detailed meaning and structure of each task")
    parser.add_argument('--seed', default=0, type=int, help="random seed")
    parser.add_argument('-betam', '--beta_mode', default="(1600,2)", type=str, help='(hidden_dim,num_layer) for BetaE relational projection')
    parser.add_argument('-boxm', '--box_mode', default="(none,0.02)", type=str, help='(offset activation,center_reg) for Query2box, center_reg balances the in_box dist and out_box dist')
    parser.add_argument('--prefix', default=None, type=str, help='prefix of the log path')
    parser.add_argument('--checkpoint_path', default=None, type=str, help='path for loading the checkpoints')
    parser.add_argument('-evu', '--evaluate_union', default="DNF", type=str, choices=['DNF', 'DM'], help='the way to evaluate union queries, transform it to disjunctive normal form (DNF) or use the De Morgan\'s laws (DM)')

    return parser.parse_args(args)

def save_model(model, optimizer, save_variable_list, args):
    '''
    Save the parameters of the model and the optimizer,
    as well as some other variables such as step and learning_rate
    '''
    
    argparse_dict = vars(args)
    with open(os.path.join(args.save_path, 'config.json'), 'w') as fjson:
        json.dump(argparse_dict, fjson)

    torch.save({
        **save_variable_list,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict()},
        os.path.join(args.save_path, 'checkpoint')
    )

def set_logger(args):
    '''
    Write logs to console and log file
    '''
    if args.do_train:
        log_file = os.path.join(args.save_path, 'train.log')
    else:
        log_file = os.path.join(args.save_path, 'test.log')

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=log_file,
        filemode='a+'
    )
    if args.print_on_screen:
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

def log_metrics(mode, step, metrics):
    '''
    Print the evaluation logs
    '''
    for metric in metrics:
        logging.info('%s %s at step %d: %f' % (mode, metric, step, metrics[metric]))

def evaluate(model, answers, args, dataloader, query_name_dict, mode, step, writer):
    '''
    Evaluate queries in dataloader
    '''
    average_metrics = defaultdict(float)
    all_metrics = defaultdict(float)

    metrics = model.test_step(model, answers, args, dataloader, query_name_dict)
    num_query_structures = 0
    num_queries = 0
    for query_structure in metrics:
        log_metrics(mode+" "+query_name_dict[query_structure], step, metrics[query_structure])
        for metric in metrics[query_structure]:
            writer.add_scalar("_".join([mode, query_name_dict[query_structure], metric]), metrics[query_structure][metric], step)
            all_metrics["_".join([query_name_dict[query_structure], metric])] = metrics[query_structure][metric]
            if metric != 'num_queries':
                average_metrics[metric] += metrics[query_structure][metric]
        num_queries += metrics[query_structure]['num_queries']
        num_query_structures += 1

    for metric in average_metrics:
        average_metrics[metric] /= num_query_structures
        writer.add_scalar("_".join([mode, 'average', metric]), average_metrics[metric], step)
        all_metrics["_".join(["average", metric])] = average_metrics[metric]
    log_metrics('%s average'%mode, step, average_metrics)

    return all_metrics

def load_data(args, tasks):
    '''
    Load queries and remove queries not in tasks
    '''
    logging.info("loading data")
    """
    train_queries = pickle.load(open(os.path.join(args.data_path, "train-queries.pkl"), 'rb'))
    train_answers = pickle.load(open(os.path.join(args.data_path, "train-answers.pkl"), 'rb')) 
    valid_queries = pickle.load(open(os.path.join(args.data_path, "train-queries.pkl"), 'rb'))
    valid_easy_answers = pickle.load(open(os.path.join(args.data_path, "train-answers.pkl"), 'rb'))
    valid_hard_answers = pickle.load(open(os.path.join(args.data_path, "train-answers.pkl"), 'rb')) 
    users_paths = pickle.load(open(os.path.join(args.data_path, "users_paths.dict"), 'rb'))
    test_answers = pickle.load(open(os.path.join(args.data_path, "test_user_dict.dict"), 'rb'))
    """
    # train
    #train_queries_1 = pickle.load(open(os.path.join(args.data_path, "train-queries-1.pkl"), 'rb'))
    #train_queries_2 = pickle.load(open(os.path.join(args.data_path, "train-queries-2.pkl"), 'rb'))
    #train_queries_3 = pickle.load(open(os.path.join(args.data_path, "train-queries-3.pkl"), 'rb'))
    #train_queries_4 = pickle.load(open(os.path.join(args.data_path, "train-queries-4.pkl"), 'rb'))
    train_queries_5 = pickle.load(open(os.path.join(args.data_path, "train-queries-5.pkl"), 'rb'))
    #train_answers_1 = pickle.load(open(os.path.join(args.data_path, "train-answers-1.pkl"), 'rb'))
    #train_answers_2 = pickle.load(open(os.path.join(args.data_path, "train-answers-2.pkl"), 'rb'))
    #train_answers_3 = pickle.load(open(os.path.join(args.data_path, "train-answers-3.pkl"), 'rb'))
    #train_answers_4 = pickle.load(open(os.path.join(args.data_path, "train-answers-4.pkl"), 'rb'))
    train_answers_5 = pickle.load(open(os.path.join(args.data_path, "train-answers-5.pkl"), 'rb'))
    #train_users_paths_1 = pickle.load(open(os.path.join(args.data_path, "users_paths_1.dict"), 'rb'))
    #train_users_paths_2 = pickle.load(open(os.path.join(args.data_path, "users_paths_2.dict"), 'rb'))
    #train_users_paths_3 = pickle.load(open(os.path.join(args.data_path, "users_paths_3.dict"), 'rb'))
    #train_users_paths_4 = pickle.load(open(os.path.join(args.data_path, "users_paths_4.dict"), 'rb'))
    train_users_paths_5 = pickle.load(open(os.path.join(args.data_path, "users_paths_5.dict"), 'rb'))
    
    train_queries_list = [train_queries_5]
    train_answers_list = [train_answers_5]
    train_users_paths_list = [train_users_paths_5]
    #train_queries_list = [train_queries_1,train_queries_2,train_queries_3,train_queries_4,train_queries_5]
    #train_answers_list = [train_answers_1,train_answers_2,train_answers_3,train_answers_4,train_answers_5]
    #train_users_paths_list = [train_users_paths_1,train_users_paths_2,train_users_paths_3,train_users_paths_4,train_users_paths_5]
    
    #test
    test_answers = pickle.load(open(os.path.join(args.data_path, "test_user_dict.dict"), 'rb'))
    """
    test_users_paths = {}
    keys = []
    items = []
    for train_users_paths in train_users_paths_list:
        keys |= train_users_paths.keys()
    for key in keys:
        for train_users_paths in train_users_paths_list:
            if key in train_users_paths:
                for item in train_users_paths[key]:
                    if item not in items:
                        items.append(item)
        test_users_paths[key] = items
    """
    test_users_paths = train_users_paths_5
    
    # remove tasks not in args.tasks
    for name in all_tasks:
        if 'u' in name:
            name, evaluate_union = name.split('-')
        else:
            evaluate_union = args.evaluate_union
        if name not in tasks or evaluate_union != args.evaluate_union:
            query_structure = name_query_dict[name if 'u' not in name else '-'.join([name, evaluate_union])]
            """
            if query_structure in train_queries:
                del train_queries[query_structure]
            if query_structure in valid_queries:
                del valid_queries[query_structure]
            """
            for train_query in train_queries_list:
                if query_structure in train_query:
                    del train_queries_list[train_query][query_structure]

    #return train_queries, train_answers,valid_queries, valid_easy_answers, valid_hard_answers, users_paths, test_answers
    return train_queries_list, train_answers_list, train_users_paths_list, test_users_paths, test_answers


def main_helper(args):
    set_global_seed(args.seed)
    tasks = args.tasks.split('.')
    for task in tasks:
        if 'n' in task and args.geo in ['box', 'vec']:
            assert False, "Q2B and GQE cannot handle queries with negation"
    if args.evaluate_union == 'DM':
        assert args.geo == 'beta', "only BetaE supports modeling union using De Morgan's Laws"

    cur_time = parse_time()
    if args.prefix is None:
        prefix = 'logs'
    else:
        prefix = args.prefix

    print ("overwritting args.save_path")
    args.save_path = os.path.join(prefix, args.data_path.split('/')[-1], args.tasks, args.geo)
    if args.geo in ['box']:
        tmp_str = "g-{}-mode-{}".format(args.gamma, args.box_mode)
    elif args.geo in ['vec']:
        tmp_str = "g-{}".format(args.gamma)
    elif args.geo == 'beta':
        tmp_str = "g-{}-mode-{}".format(args.gamma, args.beta_mode)

    if args.checkpoint_path is not None:
        args.save_path = args.checkpoint_path
    else:
        args.save_path = os.path.join(args.save_path, tmp_str, cur_time)

    if not os.path.exists(args.save_path):
        os.makedirs(args.save_path)

    print ("logging to", args.save_path)
    if not args.do_train: # if not training, then create tensorboard files in some tmp location
        writer = SummaryWriter('./logs-debug/unused-tb')
    else:
        writer_path = 'logs/'+args.data_path.split('/')[-1]+'/tensorboard'
        if not os.path.exists(writer_path):
            os.makedirs(writer_path)
        writer = SummaryWriter(writer_path)
    set_logger(args)

    with open('%s/stats.txt'%args.data_path) as f:
        entrel = f.readlines()
        nentity = int(entrel[0].split(' ')[-1])
        nrelation = int(entrel[1].split(' ')[-1])
        nitems = int(entrel[2].split(' ')[-1])
        start_item = int(entrel[3].split(' ')[-1])
    
    args.nentity = nentity
    args.nrelation = nrelation
    args.nitems = nitems
    args.start_item = start_item

    logging.info('-------------------------------'*3)
    logging.info('Geo: %s' % args.geo)
    logging.info('Data Path: %s' % args.data_path)
    logging.info('#entity: %d' % nentity)
    logging.info('#relation: %d' % nrelation)
    logging.info('#max steps: %d' % args.max_steps)
    logging.info('Evaluate unoins using: %s' % args.evaluate_union)
    
    if args.use_pretrain == 1: # pretrain
        pre_model = 'mf'
        data_name = args.data_path.split('/')[1]
        args.pretrain_embedding_dir = 'data/pretrain/%s/%s.npz' % (data_name, pre_model)

    #train_queries, train_answers, valid_queries, valid_easy_answers, valid_hard_answers, users_paths, test_answers = load_data(args, tasks) 
    train_queries_list, train_answers_list, train_users_paths_list, test_users_paths, test_answers = load_data(args, tasks) 
    
    logging.info("Training info:")
    train_path_iterator_list = []
    train_other_iterator_list = []
    path_list = ['1p', '2p', '3p', '4p', '5p']
    if args.do_train:
        for idx, train_query in enumerate(train_queries_list):
            for query_structure in train_query:
                logging.info(query_name_dict[query_structure]+": "+str(len(train_query[query_structure])))
            train_path_queries = defaultdict(set)
            for query_structure in train_query:
                if query_name_dict[query_structure] in path_list:
                    train_path_queries[query_structure] = train_query[query_structure]

            train_path_queries = flatten_query(train_path_queries)
            train_path_iterator = SingledirectionalOneShotIterator(DataLoader(
                                        TrainDataset(train_path_queries, nentity, nrelation, args.negative_sample_size, train_answers_list[idx]),
                                        batch_size=args.batch_size,
                                        shuffle=True,
                                        num_workers=args.cpu_num,
                                        collate_fn=TrainDataset.collate_fn
                                    ))
            train_path_iterator_list.append(train_path_iterator)
            train_other_iterator = SingledirectionalOneShotIterator(DataLoader(
                                        TrainOtherDataset(train_users_paths_list[idx], train_answers_list[idx], nentity, nrelation, args.negative_sample_size),
                                        batch_size=args.batch_size,
                                        num_workers=args.cpu_num,
                                        collate_fn=TrainOtherDataset.collate_fn,
                                        worker_init_fn = TrainOtherDataset.worker_init_fn
                                    ))
            train_other_iterator_list.append(train_other_iterator)

    """"
    if args.do_train:
        for query_structure in train_queries:
            logging.info(query_name_dict[query_structure]+": "+str(len(train_queries[query_structure])))
        train_path_queries = defaultdict(set)
        #train_other_queries = defaultdict(set)
        path_list = ['1p', '2p', '3p', '4p', '5p']
        for query_structure in train_queries:
            if query_name_dict[query_structure] in path_list:
                train_path_queries[query_structure] = train_queries[query_structure]
            #else:
            #    train_other_queries[query_structure] = train_queries[query_structure]
        train_path_queries = flatten_query(train_path_queries)
        train_path_iterator = SingledirectionalOneShotIterator(DataLoader(
                                    TrainDataset(train_path_queries, nentity, nrelation, args.negative_sample_size, train_answers),
                                    batch_size=args.batch_size,
                                    shuffle=True,
                                    num_workers=args.cpu_num,
                                    collate_fn=TrainDataset.collate_fn
                                ))
        #if len(train_other_queries) > 0:   
        #train_other_queries = flatten_query(train_other_queries)
        train_other_iterator = SingledirectionalOneShotIterator(DataLoader(
                                    TrainOtherDataset(users_paths, train_answers, nentity, nrelation, args.negative_sample_size),
                                    batch_size=args.batch_size,
                                    num_workers=args.cpu_num,
                                    collate_fn=TrainOtherDataset.collate_fn,
                                    worker_init_fn = TrainOtherDataset.worker_init_fn
                                ))
        #else:
        #    train_other_iterator = None
    """
    logging.info("Validation info:")
    if args.do_valid:
        for query_structure in valid_queries:
            logging.info(query_name_dict[query_structure]+": "+str(len(valid_queries[query_structure])))
        valid_queries = flatten_query(valid_queries)
        valid_dataloader = DataLoader(
            TestDataset(
                valid_queries, 
                args.nentity, 
                args.nrelation, 
            ), 
            batch_size=args.test_batch_size,
            num_workers=args.cpu_num, 
            collate_fn=TestDataset.collate_fn
        )


    logging.info("Test info:")
    if args.do_test:
        test_dataloader = DataLoader(
            TestDataset(
                #test_queries, 
                test_users_paths,
                args.nentity, 
                args.nrelation, 
            ), 
            batch_size=args.test_batch_size,
            num_workers=args.cpu_num, 
            collate_fn=TestDataset.collate_fn,
            worker_init_fn=TestDataset.worker_init_fn
        )

    model = KGReasoning(
        nentity=nentity,
        nrelation=nrelation,
        nitems=nitems,
        hidden_dim=args.hidden_dim,
        gamma=args.gamma,
        geo=args.geo,
        use_cuda = args.cuda,
        use_pretrain = args.use_pretrain, # pretrain
        pretrain_embedding_dir = args.pretrain_embedding_dir,
        box_mode=eval_tuple(args.box_mode),
        beta_mode = eval_tuple(args.beta_mode),
        test_batch_size=args.test_batch_size,
        query_name_dict = query_name_dict
    )

    logging.info('Model Parameter Configuration:')
    num_params = 0
    for name, param in model.named_parameters():
        logging.info('Parameter %s: %s, require_grad = %s' % (name, str(param.size()), str(param.requires_grad)))
        if param.requires_grad:
            num_params += np.prod(param.size())
    logging.info('Parameter Number: %d' % num_params)

    if args.cuda:
        model = model.cuda()
    
    if args.do_train:
        current_learning_rate = args.learning_rate
        optimizer = torch.optim.Adam(
            filter(lambda p: p.requires_grad, model.parameters()), 
            lr=current_learning_rate
        )
        warm_up_steps = args.max_steps // 2

    if args.checkpoint_path is not None:
        logging.info('Loading checkpoint %s...' % args.checkpoint_path)
        checkpoint = torch.load(os.path.join(args.checkpoint_path, 'checkpoint'))
        init_step = checkpoint['step']
        model.load_state_dict(checkpoint['model_state_dict'])

        if args.do_train:
            current_learning_rate = checkpoint['current_learning_rate']
            warm_up_steps = checkpoint['warm_up_steps']
            optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    else:
        logging.info('Ramdomly Initializing %s Model...' % args.geo)
        init_step = 0

    step = init_step 
    if args.geo == 'box':
        logging.info('box mode = %s' % args.box_mode)
    elif args.geo == 'beta':
        logging.info('beta mode = %s' % args.beta_mode)
    logging.info('tasks = %s' % args.tasks)
    logging.info('init_step = %d' % init_step)
    if args.do_train:
        logging.info('Start Training...')
        logging.info('learning_rate = %d' % current_learning_rate)
    logging.info('batch_size = %d' % args.batch_size)
    logging.info('hidden_dim = %d' % args.hidden_dim)
    logging.info('gamma = %f' % args.gamma)
    
    if args.do_train:
        training_logs = []
        #Training Loop
        for step in range(init_step, args.max_steps):
            if step == 2*args.max_steps//3:
                args.valid_steps *= 4
            logs = {
                'positive_sample_loss': 0.0,
                'negative_sample_loss': 0.0,
                'loss': 0.0,
            }
            for idx in range(len(train_path_iterator_list)):
                log = model.train_step(model, optimizer, train_path_iterator_list[idx], args, step)
                #for metric in log:
                #    writer.add_scalar('path_'+metric+'_'+str(idx), log[metric], step)
                if train_other_iterator_list[idx] is not None:
                    log = model.train_step(model, optimizer, train_other_iterator_list[idx], args, step)
                 #   for metric in log:
                 #       writer.add_scalar('other_'+metric+'_'+str(idx), log[metric], step)
                    log = model.train_step(model, optimizer, train_path_iterator_list[idx], args, step)
                for metric in log:
                    logs[metric] += log[metric]
            for metric in logs:
                logs[metric] /= len(train_path_iterator_list)
                writer.add_scalar(metric, log[metric], step)
            training_logs.append(logs)

            if step >= warm_up_steps:
                current_learning_rate = current_learning_rate / 5
                logging.info('Change learning_rate to %f at step %d' % (current_learning_rate, step))
                optimizer = torch.optim.Adam(
                    filter(lambda p: p.requires_grad, model.parameters()), 
                    lr=current_learning_rate
                )
                warm_up_steps = warm_up_steps * 1.5
            
            if step % args.save_checkpoint_steps == 0:
                save_variable_list = {
                    'step': step, 
                    'current_learning_rate': current_learning_rate,
                    'warm_up_steps': warm_up_steps
                }
                save_model(model, optimizer, save_variable_list, args)

            if step % args.valid_steps == 0 and step > 0:
                if args.do_valid:
                    logging.info('Evaluating on Valid Dataset...')
                    valid_all_metrics = evaluate(model, valid_easy_answers, valid_hard_answers, args, valid_dataloader, query_name_dict, 'Valid', step, writer)

                if args.do_test:
                    logging.info('Evaluating on Test Dataset...')
                    test_all_metrics = evaluate(model, test_answers, args, test_dataloader, query_name_dict, 'Test', step, writer)
                
            if step % args.log_steps == 0:
                metrics = {}
                for metric in training_logs[0].keys():
                    metrics[metric] = sum([log[metric] for log in training_logs])/len(training_logs)

                log_metrics('Training average', step, metrics)
                training_logs = []

        save_variable_list = {
            'step': step, 
            'current_learning_rate': current_learning_rate,
            'warm_up_steps': warm_up_steps
        }
        save_model(model, optimizer, save_variable_list, args)
        
    try:
        print (step)
    except:
        step = 0

    if args.do_test:
        logging.info('Evaluating on Test Dataset...')
        test_all_metrics = evaluate(model, test_answers, args, test_dataloader, query_name_dict, 'Test', step, writer)
    writer.close()
    logging.info("Training finished!!")


def main():
    main_helper(parse_args())


if __name__ == '__main__':
    main()