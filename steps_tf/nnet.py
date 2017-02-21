import tensorflow as tf
import math

def placeholder_inputs(input_dim, batch_size):
  feats_holder = tf.placeholder(tf.float32, shape=(batch_size, input_dim))
  labels_holder = tf.placeholder(tf.int32, shape=(batch_size))
  return feats_holder, labels_holder


def inference(feats_holder, input_dim, hidden_units, num_hidden_layers, output_dim, nonlin = 'relu', init = '1/d'):
  layer_in = feats_holder
  for i in range(num_hidden_layers):
    with tf.name_scope('hidden'+str(i+1)):
      dim_in = input_dim if i == 0 else hidden_units
      dim_out = hidden_units
      if init == '1/d':
        weights = tf.Variable(tf.truncated_normal([dim_in, dim_out], 
                                stddev=1.0/math.sqrt(float(dim_in))), 
                              name='weights')
      else:
        weights = tf.Variable(tf.truncated_normal([dim_in, dim_out], stddev=0.1), name='weights')
      biases = tf.Variable(tf.zeros([dim_out]), name='biases')
      if nonlin == 'relu':
        layer_out = tf.nn.relu(tf.matmul(layer_in, weights) + biases)
      elif nonlin == 'sigmoid':
        layer_out = tf.sigmoid(tf.matmul(layer_in, weights) + biases)
      elif nonlin == 'tanh':
        layer_out = tf.tanh(tf.matmul(layer_in, weights) + biases)
      layer_in = layer_out
  # Linear
  with tf.name_scope('softmax_linear'):
    if init == '1/d':
      weights = tf.Variable(tf.truncated_normal([hidden_units, output_dim], 
                              stddev=1.0/math.sqrt(float(hidden_units))), 
                            name='weights')
    else: 
      weights = tf.Variable(tf.truncated_normal([hidden_units, output_dim], stddev=0.1), name='weights')
    biases = tf.Variable(tf.zeros([output_dim]), name='biases')
    logits = tf.matmul(layer_in, weights) + biases
  return logits


def inference_from_file(feats_holder, input_dim, output_dim, init_file):
  layer_in = feats_holder
  nnet = open(init_file, 'r')
  line = nnet.readline()
  assert line.startswith('<Nnet>')
  i = 0
  for line in nnet:
    if line.startswith('</Nnet>'):
      break
    if line.startswith('<AffineTransform>'):
      info = line.split()
      dim_out = int(info[1])
      dim_in = int(info[2])
      line = nnet.readline()
      assert line.startswith('<LearnRateCoef>')
      line = nnet.readline()
      assert line.strip().startswith('[')
      line = nnet.readline().strip()
      
      mat = []
      while not line.startswith('['):
        if line.endswith(']'):
          line = line.strip(']').strip()
        mat.append(list(map(float, line.split())))
        line = nnet.readline().strip()
      w = list(zip(*mat))
      
      b = list(map(float, line.split()[1:-1]))
      
      line = nnet.readline()
      assert line.startswith('<!EndOfComponent>')

      line = nnet.readline()
      if line.startswith('<Sigmoid>'):
        with tf.name_scope('hidden'+str(i+1)):
          weights = tf.Variable(w, name='weights')
          biases = tf.Variable(b, name='biases')
          layer_out = tf.sigmoid(tf.matmul(layer_in, weights) + biases)
      elif line.startswith('<Softmax>'):
        with tf.name_scope('softmax_linear'):
          weights = tf.Variable(w, name='weights')
          biases = tf.Variable(b, name='biases')
          logits = tf.matmul(layer_in, weights) + biases

      line = nnet.readline()
      assert line.startswith('<!EndOfComponent>')

      layer_in = layer_out
      i += 1

  return logits


def loss(logits, labels):

  labels = tf.to_int64(labels)
  cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(
      logits, labels, name='xentropy')
  loss = tf.reduce_mean(cross_entropy, name='xentropy-mean')
  return loss


def training(op_conf, loss, learning_rate_holder):
  ''' learning_rate is a place holder
  loss is output of logits
  '''
  if op_conf['name'] in ['SGD', 'sgd']:
    op = tf.train.GradientDescentOptimizer(learning_rate = learning_rate_holder)
  elif op_conf['name'] == 'momentum':
    op = tf.train.MomentumOptimizer(learning_rate = learning_rate_holder, momentum = float(op_conf['momentum']))
  elif op_conf['name'] in ['adagrad', 'Adagrad']:
    op = tf.train.AdagradOptimizer(learning_rate = learning_rate_holder)
  elif op_conf['name'] in ['adam', 'Adam']:
    op = tf.train.AdamOptimizer(learning_rate = learning_rate_holder)
  train_op = op.minimize(loss)
  return train_op


def evaluation(logits, labels):

  correct = tf.nn.in_top_k(logits, labels, 1)
  return tf.reduce_sum(tf.cast(correct, tf.int32))
