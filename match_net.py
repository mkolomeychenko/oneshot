import numpy as np
mb_dim = 32
x_dim = 28*28
y_dim = 5 #5 possible classes
hid_dim = 20
n_samples_per_class = 5 #5 samples of each class
n_samples = y_dim*n_samples_per_class

data = np.load('data.npy')

def get_minibatch():
    mb_x_i = np.zeros((mb_dim,n_samples,x_dim))
    mb_y_i = np.zeros((mb_dim,n_samples))
    mb_x_hat = np.zeros((mb_dim,x_dim))
    mb_y_hat = np.zeros((mb_dim,))
    for i in range(mb_dim):
        ind = 0
        pinds = np.random.permutation(n_samples)
        classes = np.random.choice(data.shape[0],y_dim,False)
        x_hat_class = np.random.randint(y_dim)
        for j,cur_class in enumerate(classes): #each class
            example_inds = np.random.choice(data.shape[1],n_samples_per_class,False)
            for eind in example_inds:
                mb_x_i[i,pinds[ind]] = data[cur_class][eind]
                mb_y_i[i,pinds[ind]] = j
                ind +=1
            if j == x_hat_class:
                mb_x_hat[i] = data[cur_class][np.random.choice(data.shape[1])]
                mb_y_hat[i] = j
    return mb_x_i,mb_y_i,mb_x_hat,mb_y_hat
a,b,c,d = get_minibatch()



                



import tensorflow as tf
x_hat = tf.placeholder(tf.float32,shape=[None,x_dim])
x_i = tf.placeholder(tf.float32,shape=[None,n_samples,x_dim])
y_i_ind = tf.placeholder(tf.int32,shape=[None,n_samples])
y_i = tf.one_hot(y_i_ind,y_dim)
y_hat_ind = tf.placeholder(tf.int32,shape=[None])
y_hat = tf.one_hot(y_hat_ind,y_dim)
with tf.variable_scope('encode_x_hat'):
    W = tf.get_variable('W',[x_dim,hid_dim])
    b = tf.get_variable('b',[hid_dim])
    x_hat_encode = tf.nn.relu(tf.matmul(x_hat,W)+b)
with tf.variable_scope('encode_x_i'):
    W = tf.get_variable('W',[x_dim,hid_dim])
    b = tf.get_variable('b',[hid_dim])
    x_i_encode = tf.nn.relu(tf.batch_matmul(x_i,tf.tile(tf.expand_dims(W,0),[mb_dim,1,1]))+b)
x_hat_inv_mag = tf.rsqrt(tf.reduce_sum(tf.square(x_hat_encode),1))
x_i_inv_mag = tf.rsqrt(tf.reduce_sum(tf.square(x_i_encode),2))
cos_sim = tf.squeeze(tf.batch_matmul(x_i_encode,tf.expand_dims(x_hat_encode,-1)))*tf.expand_dims(x_hat_inv_mag,-1)*x_i_inv_mag
weighting = tf.nn.softmax(cos_sim)
label_prob = tf.squeeze(tf.batch_matmul(tf.expand_dims(weighting,1),y_i))

loss = -tf.log(tf.gather(label_prob,y_hat_ind))

sess = tf.Session()
sess.run(tf.initialize_all_variables())

