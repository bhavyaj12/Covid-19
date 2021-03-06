
#pip install keras

import keras
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras.layers import AveragePooling2D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing import image
import os
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from tqdm import tqdm
from sklearn.preprocessing import LabelEncoder,LabelBinarizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score,recall_score,precision_score,f1_score
from sklearn.metrics import classification_report

from google.colab import drive
drive.mount('/content/gdrive',force_remount=True)

# Commented out IPython magic to ensure Python compatibility.
# %cd "/content/gdrive/My Drive/Covid Dataset/newdata"

data = pd.read_csv('FinData.csv')

arr = data["label"].unique() 
arr

data.head

train_image = []
for i in tqdm(range(data.shape[0])):
    img = image.load_img("/content/gdrive/My Drive/Covid Dataset/newdata/" + data['id'][i], target_size=(28,28,1), grayscale=True)
    img = image.img_to_array(img)
    img = img/255
    train_image.append(img)
X = np.array(train_image)
print(type(X))

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

print('y_train shape:', y_train.shape)

model = Sequential()
model.add(Conv2D(32, kernel_size=(3, 3),activation='relu',input_shape=(28,28,1)))
model.add(MaxPooling2D(pool_size =(2, 2)))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size =(2, 2))) 
model.add(Conv2D(128, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(2, activation='softmax'))

model.compile(loss='binary_crossentropy',optimizer='Adam',metrics=['accuracy'])
model.summary()

history=model.fit(X_train, y_train, epochs=300, validation_split=0.2,batch_size=32)

plt.figure(dpi=600)
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='lower right')
plt.show()
plt.figure(dpi=600)
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper right')
plt.show()

score = model.evaluate(X_test, y_test, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

inte1 = onehot_encoder.inverse_transform(y_test)
fi1 = label_encoder.inverse_transform(inte1)
Y_pred1 = model.predict(X_test)
inte = onehot_encoder.inverse_transform(Y_pred1)
fi = label_encoder.inverse_transform(inte)
Y_pred1=np.argmax(Y_pred1, axis=1)

import seaborn as sns
target_names=['Covid19', 'Normal']
labels=np.argmax(y_test, axis=1)
con_mat = confusion_matrix(labels, Y_pred1)
con_mat_norm = np.around(con_mat.astype('float') / con_mat.sum(axis=1)[:, np.newaxis], decimals=2)
 
con_mat_df = pd.DataFrame(con_mat_norm,
                     index = target_names, 
                     columns = target_names)
figure = plt.figure(figsize=(8, 8),dpi=600)
sns.heatmap(con_mat_df, annot=True,cmap=plt.cm.Blues)
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

cm1 = confusion_matrix(labels, Y_pred1)
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

model.save("/content/gdrive/My Drive/Covid-19/Covid-CNN.h5")
