import React, { useState } from 'react';
import { View, Image, StyleSheet, Text, TouchableOpacity, Alert } from 'react-native';
import * as ImagePicker from 'expo-image-picker';

const API_URL = 'https://recycling-server.onrender.com';  // Replace with your actual URL

export default function Camera() {
  const [image, setImage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const takePhoto = async () => {
    try {
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 1,
      });

      if (!result.canceled) {
        setImage(result.assets[0].uri);
        await predict(result.assets[0].uri);
      }
    } catch (error) {
      console.error('Error taking photo:', error);
      Alert.alert('Error', 'Failed to take photo');
    }
  };

  const predict = async (uri) => {
    try {
      setIsProcessing(true);
      console.log('Starting prediction for:', uri);  // Debug log

      // Create form data
      const formData = new FormData();
      formData.append('image', {
        uri: uri,
        type: 'image/jpeg',
        name: 'photo.jpg',
      });

      console.log('Sending to server:', API_URL);  // Debug log

      // Send to server
      const response = await fetch(API_URL, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('Response status:', response.status);  // Debug log
      const text = await response.text();
      console.log('Response text:', text);  // Debug log

      try {
        const data = JSON.parse(text);
        if (data.success) {
          Alert.alert(
            'Recycling Analysis',
            `This item is: ${data.category}\n\nConfidence: ${(data.confidence * 100).toFixed(1)}%\n\nRecycling Instructions:\n• Clean the item\n• Remove any labels or caps\n• Place in ${data.category} recycling bin`
          );
        } else {
          throw new Error(data.error || 'Failed to analyze image');
        }
      } catch (parseError) {
        console.error('JSON parse error:', parseError);  // Debug log
        throw new Error('Invalid response from server');
      }

    } catch (error) {
      console.error('Prediction error:', error);
      Alert.alert('Error', 'Failed to analyze image');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity 
        style={styles.cameraButton} 
        onPress={takePhoto}
        disabled={isProcessing}
      >
        <Text style={styles.cameraButtonText}>
          {isProcessing ? 'Processing...' : 'Take Photo'}
        </Text>
      </TouchableOpacity>

      {image && (
        <View style={styles.imageContainer}>
          <Image source={{ uri: image }} style={styles.image} />
          {isProcessing && (
            <View style={styles.processingContainer}>
              <Text style={styles.processingText}>Analyzing image...</Text>
            </View>
          )}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
    backgroundColor: '#fff',
  },
  cameraButton: {
    backgroundColor: '#4CAF50',
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: 25,
    marginBottom: 20,
  },
  cameraButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  imageContainer: {
    alignItems: 'center',
  },
  image: {
    width: 300,
    height: 300,
    borderRadius: 10,
    marginBottom: 10,
  },
  processingContainer: {
    position: 'absolute',
    top: '50%',
    backgroundColor: 'rgba(0,0,0,0.7)',
    padding: 15,
    borderRadius: 10,
  },
  processingText: {
    color: 'white',
    fontSize: 16,
  }
});