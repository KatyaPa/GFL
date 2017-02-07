import tensorflow as tf
import numpy as np

tf.reset_default_graph()

# Create input data
X = np.random.randn(2, 10, 8)
print X
print X.shape

# The second example is of length 6 
X[1,6:] = 0
print X
X_lengths = [10, 6]

cell = tf.nn.rnn_cell.LSTMCell(num_units=64, state_is_tuple=True)

outputs, states  = tf.nn.bidirectional_dynamic_rnn(
    cell_fw=cell,
    cell_bw=cell,
    dtype=tf.float64,
    sequence_length=X_lengths,
    inputs=X)

output_fw, output_bw = outputs
states_fw, states_bw = states

result = tf.contrib.learn.run_n(
    {"output_fw": output_fw, "output_bw": output_bw, "states_fw": states_fw, "states_bw": states_bw},
    n=1,
    feed_dict=None)

print(result[0]["output_fw"].shape)
print(result[0]["output_bw"].shape)
print(result[0]["states_fw"].h.shape)
print(result[0]["states_bw"].h.shape)
