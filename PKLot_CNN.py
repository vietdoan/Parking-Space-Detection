from __future__ import print_function
import os
from scipy import misc
import random
import numpy as np
import keras
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras.layers.normalization import BatchNormalization
from keras.preprocessing.image import ImageDataGenerator

file_dirs = []
for root, dirs, files in os.walk("/data/vietdv/PKLot/PKLotSegmented/UFPR04", topdown=False):
    for name in files:
        file_dirs.append(os.path.join(root, name))


random.shuffle(file_dirs)
num_samples = len(file_dirs)
X = []
Y = []

for root, dirs, files in os.walk("/data/vietdv/OwnCollection/non-vehicles", topdown=False):
    for name in files:
        dire = os.path.join(root, name)
        f = misc.imread(dire)
        f = misc.imresize(f, (48, 64))
        X.append(f)
        Y.append(0)

for root, dirs, files in os.walk("/data/vietdv/OwnCollection/vehicles", topdown=False):
    for name in files:
        dire = os.path.join(root, name)
        f = misc.imread(dire)
        f = misc.imresize(f, (48, 64))
        X.append(f)
        Y.append(1)

for root, dirs, files in os.walk("/data/vietdv/cars_train", topdown=False):
    for name in files:
        dire = os.path.join(root, name)
        f = misc.imread(dire)
        if (f.ndim == 2):
            continue
        f = misc.imresize(f, (48, 64))
        X.append(f)
        Y.append(1)

for i in range(0, num_samples):
    f = misc.imread(file_dirs[i])
    f = misc.imresize(f, (48, 64))
    X.append(f)
    folders = file_dirs[i].split('/')
    label = 1 if folders[len(folders) - 2] == 'Occupied' else 0
    Y.append(label)

for root, dirs, files in os.walk("/data/vietdv/cars_test", topdown=False):
    for name in files:
        dire = os.path.join(root, name)
        f = misc.imread(dire)
        if (f.ndim == 2):
            continue
        f = misc.imresize(f, (48, 64))
        X.append(f)
        Y.append(1)
print("complete reading")
num_samples = np.shape(X)[0]
X = np.array(X)
Y = np.array(Y)
num_validate = 10000
num_test = 10000
num_val_test = num_validate + num_test
(x_train, y_train) = (X[:num_samples - num_val_test], Y[:num_samples - num_val_test])
(x_test, y_test) = (X[num_samples - num_val_test:num_samples - num_test],
                    Y[num_samples - num_val_test:num_samples - num_test])

batch_size = 512
num_classes = 2
epochs = 20
img_rows, img_cols = 48, 64

y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)

x_train = x_train.astype('float64')
x_test = x_test.astype('float64')
pk = np.reshape(x_train, (-1, 3))
mean = np.mean(pk, 0)
std = np.std(pk, 0)
del pk
x_test -= mean
x_test /= (std + 1e-9)
x_train -= mean
x_train /= (std + 1e-9)
x_test /= 255
x_train /= 255
print('mean and standard deviation:')
print(mean)
print(std)
if keras.backend.image_data_format() == 'channels_first':
    input_shape = (3, img_rows, img_cols)
else:
    input_shape = (img_rows, img_cols, 3)

model = Sequential()
model.add(Conv2D(10, kernel_size=(5, 5),
                 activation='relu',
                 input_shape=input_shape))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(20, kernel_size=(5, 5),
                 activation='relu',
                 input_shape=input_shape))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(30, kernel_size=(5, 5),
                 activation='relu',
                 input_shape=input_shape))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Flatten())
model.add(Dense(30, activation='relu'))
model.add(Dense(20, activation='relu'))
model.add(Dense(10, activation='relu'))
model.add(Dense(2, activation='softmax'))

model.compile(loss=keras.losses.categorical_crossentropy,
              optimizer=keras.optimizers.Adadelta(),
              metrics=['accuracy'])
model.fit(x_train, y_train,
          batch_size=batch_size,
          epochs=epochs,
          verbose=2,
          validation_data=(x_test, y_test))
score = model.evaluate(x_test, y_test, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

from keras.models import load_model
model.save('PKLot2.h5')

x_val, y_val = (X[num_samples - num_test:], Y[num_samples - num_test:])
x_val = np.array(x_val)
y_val = np.array(y_val)
x_val = x_val.astype('float64')
x_val = (x_val - mean) / (std + 1e-9)
x_val /= 255
prediction = model.predict(x_val)
y_val = keras.utils.to_categorical(y_val, num_classes)
acc_val = np.mean(np.round(prediction) == y_val)
print(acc_val)
