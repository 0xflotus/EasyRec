# -*- encoding:utf-8 -*-
# Copyright (c) Alibaba, Inc. and its affiliates.
import csv
import json
import logging
import os
import shutil

import numpy as np
import tensorflow as tf

from easy_rec.python.inference.predictor import Predictor
from easy_rec.python.utils import test_utils
from easy_rec.python.utils.test_utils import RunAsSubprocess


class PredictorTest(tf.test.TestCase):

  def setUp(self):
    self.gpus = test_utils.get_available_gpus()
    self.assertTrue(len(self.gpus) > 0, 'no available gpu on this machine')
    logging.info('available gpus %s' % self.gpus)
    test_utils.set_gpu_id(self.gpus[0])
    logging.info('Testing %s.%s' % (type(self).__name__, self._testMethodName))
    self._test_path = 'data/test/inference/taobao_infer_data.txt'

  def tearDown(self):
    test_utils.set_gpu_id(None)

  @RunAsSubprocess
  def test_pred_list(self):
    predictor = Predictor('data/test/inference/tb_multitower_export/')
    with open(self._test_path, 'r') as fin:
      reader = csv.reader(fin)
      inputs = []
      for row in reader:
        inputs.append(row[2:])
      output_res = predictor.predict(inputs, batch_size=32)
      self.assertTrue(len(output_res) == 100)

  @RunAsSubprocess
  def test_lookup_pred(self):
    predictor = Predictor('data/test/inference/lookup_export')
    lookup_pred_path = 'data/test/inference/lookup_data_test80.csv'
    with open(lookup_pred_path, 'r') as fin:
      reader = csv.reader(fin)
      inputs = []
      for row in reader:
        inputs.append(row[1:])
      output_res = predictor.predict(inputs, batch_size=32)
      self.assertTrue(len(output_res) == 80)

  @RunAsSubprocess
  def test_pred_dict(self):
    predictor = Predictor('data/test/inference/tb_multitower_export/')
    field_keys = [
        'pid', 'adgroup_id', 'cate_id', 'campaign_id', 'customer', 'brand',
        'user_id', 'cms_segid', 'cms_group_id', 'final_gender_code',
        'age_level', 'pvalue_level', 'shopping_level', 'occupation',
        'new_user_class_level', 'tag_category_list', 'tag_brand_list', 'price'
    ]
    with open(self._test_path, 'r') as fin:
      reader = csv.reader(fin)
      inputs = []
      for row in reader:
        inputs.append({f: row[fid + 2] for fid, f in enumerate(field_keys)})
      output_res = predictor.predict(inputs, batch_size=32)
      self.assertTrue(len(output_res) == 100)

  @RunAsSubprocess
  def test_pred_placeholder_named_by_input(self):
    predictor = Predictor(
        'data/test/inference/tb_multitower_placeholder_rename_export/')
    field_keys = [
        'pid', 'adgroup_id', 'cate_id', 'campaign_id', 'customer', 'brand',
        'user_id', 'cms_segid', 'cms_group_id', 'final_gender_code',
        'age_level', 'pvalue_level', 'shopping_level', 'occupation',
        'new_user_class_level', 'tag_category_list', 'tag_brand_list', 'price'
    ]
    with open(self._test_path, 'r') as fin:
      reader = csv.reader(fin)
      inputs = []
      for row in reader:
        line_input = {}
        for fid, f in enumerate(field_keys):
          if f in ['tag_category_list', 'tag_brand_list']:
            line_input[f] = ['12', '23']
          else:
            line_input[f] = row[fid + 2]
        inputs.append(line_input)
      output_res = predictor.predict(inputs, batch_size=32)
      self.assertTrue(len(output_res) == 100)

  @RunAsSubprocess
  def test_fm_pred_list(self):
    predictor = Predictor('data/test/inference/fm_export/')
    with open(self._test_path, 'r') as fin:
      reader = csv.reader(fin)
      inputs = []
      for row in reader:
        inputs.append(row[2:])
      output_res = predictor.predict(inputs, batch_size=32)
      self.assertTrue(len(output_res) == 100)

  @RunAsSubprocess
  def test_fm_pred_dict(self):
    predictor = Predictor('data/test/inference/fm_export/')
    field_keys = [
        'pid', 'adgroup_id', 'cate_id', 'campaign_id', 'customer', 'brand',
        'user_id', 'cms_segid', 'cms_group_id', 'final_gender_code',
        'age_level', 'pvalue_level', 'shopping_level', 'occupation',
        'new_user_class_level', 'tag_category_list', 'tag_brand_list', 'price'
    ]
    with open(self._test_path, 'r') as fin:
      reader = csv.reader(fin)
      inputs = []
      for row in reader:
        inputs.append({f: row[fid + 2] for fid, f in enumerate(field_keys)})
      output_res = predictor.predict(inputs, batch_size=32)
      self.assertTrue(len(output_res) == 100)


class PredictorTestOnDS(tf.test.TestCase):

  def setUp(self):
    self._test_input_path = 'data/test/inference/taobao_infer_data.txt'
    self._test_output_path = 'data/test/inference/taobao_infer_result'

    self.gpus = test_utils.get_available_gpus()
    self.assertTrue(len(self.gpus) > 0, 'no available gpu on this machine')
    logging.info('available gpus %s' % self.gpus)
    test_utils.set_gpu_id(self.gpus[0])
    logging.info('Testing %s.%s' % (type(self).__name__, self._testMethodName))

  def tearDown(self):
    if (os.path.exists(self._test_output_path)):
      shutil.rmtree(self._test_output_path)
    test_utils.set_gpu_id(None)

  @RunAsSubprocess
  def test_local_pred(self):
    predictor = Predictor('data/test/inference/tb_multitower_export/')
    predictor.predict_impl(
        self._test_input_path,
        self._test_output_path,
        reserved_cols='ALL_COLUMNS',
        output_cols='ALL_COLUMNS',
        slice_id=0,
        slice_num=1,
        input_sep=',',
        output_sep=';')

    with open(self._test_output_path + '/slice_0.csv', 'r') as f:
      output_res = f.readlines()
      self.assertTrue(len(output_res) == 101)


class PredictorTestV2(tf.test.TestCase):

  def setUp(self):
    self.gpus = test_utils.get_available_gpus()
    self.assertTrue(len(self.gpus) > 0, 'no available gpu on this machine')
    logging.info('available gpus %s' % self.gpus)
    test_utils.set_gpu_id(self.gpus[0])
    logging.info('Testing %s.%s' % (type(self).__name__, self._testMethodName))

  def tearDown(self):
    test_utils.set_gpu_id(None)

  @RunAsSubprocess
  def test_pred_multi(self):
    predictor = Predictor('data/test/inference/fg_export_multi')
    test_path = 'data/test/rtp/taobao_test_feature.txt'
    with open(test_path, 'r') as fin:
      inputs = []
      for line_str in fin:
        line_str = line_str.strip()
        line_toks = line_str.split(';')
        feature = line_toks[-1]
        feature = feature.split('\002')
        inputs.append(feature)
      output_res = predictor.predict(inputs, batch_size=32)
      self.assertTrue(len(output_res) == 10000)
    with open('data/test/rtp/taobao_fg_pred.out', 'r') as fin:
      for line_id, line_str in enumerate(fin):
        line_str = line_str.strip()
        line_pred = json.loads(line_str)
        self.assertTrue(
            np.abs(line_pred['probs'] - output_res[line_id]['probs']) < 5e-6)

  @RunAsSubprocess
  def test_pred_single(self):
    predictor = Predictor('data/test/inference/fg_export_single')
    test_path = 'data/test/rtp/taobao_test_feature.txt'
    with open(test_path, 'r') as fin:
      inputs = []
      for line_str in fin:
        line_str = line_str.strip()
        line_toks = line_str.split(';')
        feature = line_toks[-1]
        inputs.append(feature)
      output_res = predictor.predict(inputs, batch_size=32)
    with open('data/test/rtp/taobao_fg_pred.out', 'r') as fin:
      for line_id, line_str in enumerate(fin):
        line_str = line_str.strip()
        line_pred = json.loads(line_str)
        self.assertTrue(
            np.abs(line_pred['probs'] - output_res[line_id]['probs']) < 5e-5)


if __name__ == '__main__':
  tf.test.main()
