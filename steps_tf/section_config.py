def str2boolean(string):
  if string in ['True', 'true', 'TRUE']:
    return True
  elif string in ['False', 'false', 'FALSE']:
    return False


def parse(config_tuple):
  config_dict = dict(config_tuple)
  config_parsed = {}
  for i in config_dict.keys():
    if i in ['min_iters', 'keep_lr_iters', 'max_iters', 'context_width', 
             'batch_size', 'hidden_units', 'num_hidden_layers', 'num_cells',
             'max_length', 'sliding_window', 'jitter_window', 'bottleneck_dim',
             'num_iters', 'num_gpus', 'num_hidden_layers_after_bn', 'num_proj',
             'pooling_units', 'asr_hidden_layers', 'asr_hidden_units',
             'sid_hidden_layers', 'sid_hidden_units', 'max_split_data_size',
             'split_per_iter', 'gpu_id']:
      config_parsed[i] = int(config_dict[i])
    elif i in ['halving_factor', 'start_halving_impr', 'end_halving_impr', 
               'initial_learning_rate', 'final_learning_rate', 'momentum', 
               'keep_prob', 'keep_in_prob', 'keep_out_prob', 'alpha', 'beta', 
               'param_stddev_factor', 'hid_bias_range', 'noise_ratio']:
      config_parsed[i] = float(config_dict[i])
    elif i in ['batch_norm', 'affine_batch_norm', 'with_softmax', 'use_peepholes', 
               'clip_gradients', 'use_std', 'with_nonlin', 'sid_batch_norm', 'fit_buckets',
               'loop_mode', 'clean_up', 'norm_before_pooling', 'variable_length',
               'edit_model']:
      config_parsed[i] = str2boolean(config_dict[i])
    elif i in ['nonlin', 'op_type', 'nnet_arch', 'lstm_type', 'feat_type', 
               'delta_opts', 'tmp_dir', 'cmvn_type', 'embedding_layers', 
               'nnet_proto', 'feat_dir', 'gpu_ids', 'mode', 'scheduler_type']:
      config_parsed[i] = config_dict[i]
    elif i in ['buckets', 'buckets_tr']: # for list of integers
      config_parsed[i] = [int(x) for x in config_dict[i].split(',')]
    else:
      raise RuntimeError('section_config.parse: config field %s not supported' % i)

  return config_parsed
