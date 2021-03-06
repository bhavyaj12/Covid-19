
pip install keras

import gc
import math
import cv2
import glob
import os, shutil
import numpy as np 
import pandas as pd 
from PIL import Image
import keras
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder,LabelBinarizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score,recall_score,precision_score,f1_score
from sklearn.metrics import classification_report
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten,BatchNormalization
from tensorflow.keras.layers import Conv2D, MaxPooling2D,AveragePooling2D, GlobalAveragePooling2D
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing import image
from tensorflow.keras.layers import Input
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from tqdm import tqdm
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau

from google.colab import drive
drive.mount('/content/gdrive', force_remount=True)

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/gdrive/My Drive/Covid Dataset/newdata

data = pd.read_csv('FinData.csv')
arr = data["label"].unique() 
arr

from skimage.filters import unsharp_mask

for i in tqdm(range(1,2)):
    img = image.load_img("/content/gdrive/My Drive/Covid Dataset/newdata/" + data['id'][i], target_size=(224,224,3), grayscale=False)
    unsharp_image = unsharp_mask(img, radius=5, amount=2)
    equalized_image = exposure.equalize_hist(unsharp_image)
    equalized_image = image.img_to_array(equalized_image)    
    equalized_image = equalized_image/255
    check = equalized_image*255

fig, axes = plt.subplots(nrows=1, ncols=2,
                         sharex=True, sharey=True, figsize=(10, 10))
ax = axes.ravel()

ax[0].imshow(img)
ax[0].set_title('Original image')
ax[1].imshow(check)
ax[1].set_title('Enhanced image')
plt.show()

train_image = []
for i in tqdm(range(data.shape[0])):
    img = image.load_img("/content/gdrive/My Drive/Covid Dataset/newdata/" + data['id'][i], target_size=(224,224,3), grayscale=False)
    unsharp_image = unsharp_mask(img, radius=5, amount=2)
    equalized_image = exposure.equalize_hist(unsharp_image)
    equalized_image = image.img_to_array(equalized_image)    
    equalized_image = equalized_image/255
    train_image.append(equalized_image)
X = np.array(train_image)
print(type(X))
print(img)

print('x_train shape:', X.shape)

y_init=data['label'].values
def prepare_labels(y):
    values = np.array(y)
    label_encoder = LabelEncoder()
    integer_encoded = label_encoder.fit_transform(values)
    #print(integer_encoded.shape)

    onehot_encoder = OneHotEncoder(sparse=False)
    integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
    onehot_encoded = onehot_encoder.fit_transform(integer_encoded)
    #print(onehot_encoded)

    y = onehot_encoded
    #print(y)
    return y, label_encoder, onehot_encoder
y, label_encoder, onehot_encoder = prepare_labels(y_init)
y.shape

X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42, test_size=0.2)

print('y_train shape:', y.shape)

from tensorflow.keras.applications import DenseNet121
from tensorflow.keras.models import Model

baseModel = DenseNet121(weights="imagenet", include_top=False,
	input_tensor=Input(shape=(224, 224, 3)))

for layer in baseModel.layers:
	layer.trainable = False

headModel = baseModel.output
headModel = Flatten(name="flatten")(headModel)
headModel = Dense(256, activation='relu')(headModel)
headModel = Dropout(0.3)(headModel)
headModel = Dense(128, activation='relu')(headModel)
headModel = Dropout(0.4)(headModel)
headModel = Dense(2, activation='softmax')(headModel)
model = Model(inputs=baseModel.input, outputs=headModel)

model.summary()

from tensorflow.keras.optimizers import Adamax
model.compile(loss='binary_crossentropy',optimizer='adamax',metrics=['accuracy'])

history=model.fit(X_train, y_train, epochs=300, validation_split=0.2,batch_size=32)

score = model.evaluate(X_test, y_test, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

predictions = model.predict(X_test)

#summarize the hostory for loss
plt.figure(dpi=600)
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
# summarize history for accuracy
plt.figure(dpi=600)
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

inte1 = onehot_encoder.inverse_transform(y_test)
fi1 = label_encoder.inverse_transform(inte1)
Y_pred = model.predict(X_test)
inte = onehot_encoder.inverse_transform(Y_pred)
fi = label_encoder.inverse_transform(inte)

import seaborn as sns
labels=np.argmax(y_test, axis=1)
pred=np.argmax(predictions, axis=1)
target_names=['Covid', 'Normal']
con_mat = confusion_matrix(labels, pred)
con_mat_norm = np.around(con_mat.astype('float') / con_mat.sum(axis=1)[:, np.newaxis], decimals=2)
 
con_mat_df = pd.DataFrame(con_mat_norm,
                     index = target_names, 
                     columns = target_names)
figure = plt.figure(figsize=(8, 8),dpi=600)
sns.heatmap(con_mat_df, annot=True,cmap=plt.cm.BuPu)
plt.tight_layout()
plt.ylabel('True label')
plt.xlabel('Predicted label')
plt.show()

print("Precision Score : ",precision_score(fi1, fi, pos_label=arr[0], average='binary'))
print("Recall Score : ",recall_score(fi1, fi, pos_label=arr[0],average='binary'))
print('Accuracy Score : ' + str(accuracy_score(fi1,fi)))
print('F1 Score : ' + str(f1_score(fi1,fi, pos_label=arr[0],average='binary')))

print('Classification Report')
target_names = ['Covid', 'Normal']
print(classification_report(fi1, fi, target_names=target_names))

cm1=confusion_matrix(labels,pred)
sensitivity1 = cm1[0,0]/(cm1[0,0]+cm1[0,1])
print('Sensitivity : ', sensitivity1 )

specificity1 = cm1[1,1]/(cm1[1,0]+cm1[1,1])
print('Specificity : ', specificity1)

print(fi1)
print(len(fi1))
print(fi)
print(len(fi))
tfi1=[]
tfi=[]

for i in fi1:
  if(i==2):
    tfi1.append(0)
  if(i==1):
    tfi1.append(1)

for i in fi:
  if(i==2):
    tfi.append(0)
  if(i==1):
    tfi.append(1)

print(tfi1)
print(len(tfi1))
print(tfi)
print(len(tfi))

from sklearn.metrics import roc_curve
from sklearn.metrics import auc

fpr, tpr, thresholds = roc_curve(tfi1, tfi,pos_label=arr[0])
auc_keras = auc(fpr, tpr)
plt.figure(dpi=600)
plt.plot([0, 1], [0, 1], 'k--')
plt.plot(fpr, tpr, label='Model (area = {:.3f})'.format(auc_keras))
plt.xlabel('False positive rate')
plt.ylabel('True positive rate')
plt.title('ROC curve')
plt.legend(loc='best')
plt.show()

from sklearn.metrics import mean_absolute_error
print(mean_absolute_error(fi1, fi))

from sklearn.metrics import mean_squared_error
print(mean_squared_error(fi1, fi, squared=False))

model.save("/content/gdrive/My Drive/Covid-19/DenseNetUnsharp.h5")

