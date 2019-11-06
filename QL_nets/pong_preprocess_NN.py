import numpy as np
from keras.layers import Dense, Input, Flatten, Lambda
from keras.models import Model
from keras import optimizers
from keras import metrics
from keras.utils import HDF5Matrix
from keras.callbacks import ModelCheckpoint

# Define NN preprocessor

# With the functional API we need to define the inputs.
frames = Input((210, 160, 3), name='frames')

# Assuming that the input frames are still encoded from 0 to 255. Transforming to [0, 1].
normalized = Lambda(lambda x: x / 255.0)(frames)

# Flatten the image.
flattened = Flatten()(normalized)

# Hidden layer
hidden_1 = Dense(200, activation='relu')(flattened)
hidden_2 = Dense(200, activation='relu')(hidden_1)
hidden_3 = Dense(200, activation='relu')(hidden_2)

# Output layer
output = Dense(6, activation='linear')(hidden_3)

model = Model(inputs=frames, outputs=output)
ADAM = optimizers.Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)
model.compile(optimizer=ADAM,
              loss='mse',
              metrics=['mae'])

# Load data
x_train = HDF5Matrix('/Users/Guillermo/OneDrive - University of Edinburgh/QL_nets/data_preprocessor_pong.h5', 'X_train', 0, 120000)
y_train = HDF5Matrix('/Users/Guillermo/OneDrive - University of Edinburgh/QL_nets/data_preprocessor_pong.h5', 'Y_train', 0, 120000)

x_val = HDF5Matrix('/Users/Guillermo/OneDrive - University of Edinburgh/QL_nets/data_preprocessor_pong.h5', 'X_train', 120000, 160000)
y_val = HDF5Matrix('/Users/Guillermo/OneDrive - University of Edinburgh/QL_nets/data_preprocessor_pong.h5', 'Y_train', 120000, 160000)

# Define callback to save weights after each epoch
check_point = ModelCheckpoint('pong_preprocessor_weights.{epoch:02d}-{val_loss:.2f}.hdf5',
                              monitor='val_loss',
                              verbose=0,
                              save_best_only=True,
                              save_weights_only=True,
                              mode='auto',
                              period=1)
# train!
model.fit(x_train, y_train,
          shuffle=False,
          epochs=10, verbose=1,
          batch_size=32,
          callbacks=[check_point],
          validation_data=(x_val, y_val))

