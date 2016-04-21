# Written by: Erick Cobos T. (a01184587@itesm.mx)
# Date: April 2016

""" Quick script to eval images using a trained network
Example:
	>>> import eval
	>>> prediction = eval.evaluate("my_image.png", "my_label.png")

Note:
	Call tf.reset_default_graph() to run it twice in the same python terminal.
	Otherwise, restore will not work.
"""
import tensorflow as tf
import model
import scipy.misc
import numpy as np

checkpoint_dir = "checkpoint/run3"

def load_image(image_path):
	""" Load png image as tensor and whiten it."""
	image_content = tf.read_file(image_path)
	image = tf.image.decode_png(image_content)
	image = tf.image.per_image_whitening(image)
	return image
	
def post(logits, label, threshold):
	"""Creates segmentation assigning everything over the threshold a value of 
	255, anythig equals to background in label as 0 and anythign else 127. 
	
	Using the label may seem like cheating but the background part of the label 
	was generated by thresholding the original image to zero, so it is as if i
	did that here. Just that it is more cumbersome. Not that important either as
	I calculate IOU for massses and not for backgorund or breats tissue."""
	thresholded = np.ones(logits.shape, dtype='uint8') * 127
	thresholded[logits >= threshold] = 255
	thresholded[label == 0] = 0
	return thresholded
	
def IOU(segmentation, label):
	"""Intersection over union"""
	intersection = np.logical_and(segmentation == 255, label == 255)
	union = np.logical_or(segmentation == 255, label == 255)
	iou = np.sum(intersection)/np.sum(union)
	return iou
	
def evaluate(image_path, label_path):
	""" Loads network, reads image and returns IOU."""
	# Load image and label
	image = load_image(image_path)
	label = scipy.misc.imread(label_path)
	
	# Define the model
	prediction = model.model(image, drop=False)
	
	# Get a saver
	saver = tf.train.Saver()

	# Launch the graph
	with tf.Session() as sess:
		# Restore variables
		checkpoint_path = tf.train.latest_checkpoint(checkpoint_dir)
		saver.restore(sess, checkpoint_path)
		model.log("Variables restored from:", checkpoint_path)
	
		logits = prediction.eval()
		
		segmentation = post(logits, label, threshold = -1)
		
		iou = IOU(segmentation, label)
		
		print("iou =", iou)
		
	return iou