'use strict';
import React, { Component } from 'react';
import BasicView, { cameraImage } from "./Components";
import {
  AppRegistry,
  Dimensions,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  Button,
  Image
} from 'react-native';
import { RNCamera } from 'react-native-camera';
import RNFS from 'react-native-fs'
import { createStackNavigator } from 'react-navigation';

class HomeScreen extends BasicView {
  render() {
    const { navigate } = this.props.navigation;
    return (
      <View style={styles.maincontainer}>
        <TouchableOpacity style={styles.button} onPress={()=>{navigate('PhotoTaker')}}>
          <Image style={ styles.stretch} source={ require("./assets/camera.png") }/>
          <Text>Take A photo of historical landmark</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.button} onPress={()=>{navigate('Map')}}>
          <Image style={ styles.stretch} source={ require("./assets/map.png") }/>
          <Text style={{justifyContent: 'center'}}>Map of taken photo</Text>
        </TouchableOpacity>
      </View>
    );
  }
}

class PhotoTakerScreen extends BasicView {
  render() {
    return (
      <View style={styles.container}>
        <RNCamera
            ref={ref => {
              this.camera = ref;
            }}
            style = {styles.preview}
            type={RNCamera.Constants.Type.back}
            flashMode={RNCamera.Constants.FlashMode.off}
            permissionDialogTitle={'Permission to use camera'}
            permissionDialogMessage={'We need your permission to use your camera phone'}
        />
        <View style={{flex: 0, flexDirection: 'row', justifyContent: 'center',}}>
        <TouchableOpacity
            onPress={this.takePicture.bind(this)}
            style = {styles.capture}
        >
            <Text style={{fontSize: 14}}> SNAP </Text>
        </TouchableOpacity>
        </View>
      </View>
    );
  }

  takePicture = async function() {
    const { navigate } = this.props.navigation;
    if (this.camera) {
      const options = { quality: 0.5, base64: true };
      const data = await this.camera.takePictureAsync(options)
      const base64image = await RNFS.readFile(data.uri, 'base64');
      navigate("Home");
      fetch("http://192.168.1.245:8888/photo", {
        method: 'POST',
        headers: new Headers({
             'Content-Type': 'application/x-www-form-urlencoded', // <-- Specifying the Content-Type
        }),
        body: base64image // <-- Post parameters
      })
      .then((response) => /*response.json())
      .then((responseJson) =>*/ {
        alert(response);
      })
      .catch((error) => {
        console.error(error);
      });;
    }
  };
}

class MapScreen extends BasicView {
  render() {
    return (
      <View style={{ flex: 1, alignItems: 'center', justifyContent: "center" }}>
        <Text>Here will be map of taken photo</Text>
      </View>
    );
  }
}

const styles = StyleSheet.create({
  maincontainer: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'row'
  },
  button: {
    backgroundColor: '#fff',
    borderRadius: 20,
    padding: 10,
    marginLeft: 12,
    marginRight: 12,
    marginBottom: 20,
    alignItems: 'center',
    width: 110,
  },
  container: {
    flex: 1,
    flexDirection: 'column',
    backgroundColor: 'black'
  },
  preview: {
    flex: 1,
    justifyContent: 'flex-end',
    alignItems: 'center'
  },
  capture: {
    flex: 0,
    backgroundColor: '#fff',
    borderRadius: 5,
    padding: 15,
    paddingHorizontal: 20,
    alignSelf: 'center',
    margin: 20
  },
  stretch: {
    width: 100,
    height: 100
  }
});

const RootStack = createStackNavigator(
  {
    Home: HomeScreen,
    PhotoTaker: PhotoTakerScreen,
    Map: MapScreen
  },
  {
    initialRouteName: 'Home',
  }
);

export default class App extends React.Component {
  render() {
    return <RootStack />;
  }
}