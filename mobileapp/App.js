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
  Image,
  DeviceEventEmitter,
  Platform,
  Linking
} from 'react-native';
import { RNCamera } from 'react-native-camera';
import RNFS from 'react-native-fs'
import { createStackNavigator } from 'react-navigation';

import { ReactNativeHeading } from 'NativeModules'

const host = "http://192.168.1.245:8888";

class HomeScreen extends BasicView {
  render() {
    const { navigate } = this.props.navigation;
    return (
      <View style={styles.maincontainer}>
        <TouchableOpacity style={styles.button} onPress={() => { navigate('PhotoTaker') }}>
          <Image style={styles.stretch} source={require("./assets/camera.png")} />
          <Text>Take a photo to recognize</Text>
        </TouchableOpacity>
      </View>
    );
  }
}

class PhotoTakerScreen extends BasicView {
  constructor(props) {
    super(props);
    this.heading = 0;
    this.state = {
      latitude: null,
      longitude: null,
      accuracy: null,
      error: null,
    };
  }
  render() {
    return (
      <View style={styles.container}>
        <RNCamera
          ref={ref => {
            this.camera = ref;
          }}
          style={styles.preview}
          type={RNCamera.Constants.Type.back}
          flashMode={RNCamera.Constants.FlashMode.off}
          permissionDialogTitle={'Permission to use camera'}
          permissionDialogMessage={'We need your permission to use your camera phone'}
        />
        <View style={{ flex: 0, flexDirection: 'row', justifyContent: 'center', }}>
          <TouchableOpacity
            onPress={this.takePicture.bind(this)}
            style={styles.capture}
          >
            <Text style={{ fontSize: 14 }}> SNAP </Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  takePicture = async function () {
    const { navigate } = this.props.navigation;
    if (this.camera) {
      const lastHeading = this.heading;
      const longitude = this.state.longitude;
      const latitude = this.state.latitude;
      const accuracy = this.state.accuracy;
      const options = { quality: 0.5, base64: true };
      const data = await this.camera.takePictureAsync(options)
      navigate("Load", {
        heading: lastHeading,
        longitude: longitude,
        latitude: latitude,
        accuracy: accuracy,
        dataUri: data.uri
      });
    }
  };

  componentDidMount() {
    this.watchId = navigator.geolocation.watchPosition(
      (position) => {
        this.setState({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: Math.round(position.coords.accuracy * 10) /10,
          error: null,
        });
      },
      (error) => this.setState({ error: error.message }),
      { enableHighAccuracy: false, timeout: 20000, maximumAge: 1000, distanceFilter: 10 },
    );

    ReactNativeHeading.start(1)
      .then(didStart => {
        this.setState({
          headingIsSupported: didStart,
        })
      })

    DeviceEventEmitter.addListener('headingUpdated', data => {
      this.heading = data;
    });

  }
  componentWillUnmount() {
    navigator.geolocation.clearWatch(this.watchId);
    ReactNativeHeading.stop();
    DeviceEventEmitter.removeAllListeners('headingUpdated');
  }
}

class LoadingScreen extends BasicView {
  render() {
    this.sendPicture();
    return (
      <View style={{ flex: 1, alignItems: 'center', justifyContent: "center", backgroundColor: "#ffffff" }}>
        <Image
          style={{ width: 360, height: 480 }}
          source={require("./assets/loading.gif")}
        />
        <Text>Please wait until task is processed</Text>
      </View>
    )
  }
  sendPicture = async function () {
    const { navigation } = this.props;
    const { navigate } = this.props.navigation;
    const heading = navigation.getParam('heading', '');
    const longitude = navigation.getParam('longitude', 'Could not load');
    const latitude = navigation.getParam('latitude', 'Could not load');
    const accuracy = navigation.getParam('accuracy', 'Could not load');
    const dataUri = navigation.getParam('dataUri', '');
    const base64image = await RNFS.readFile(dataUri, 'base64');
    fetch(host + "/photo", {
      method: 'POST',
      headers: new Headers({
        'Content-Type': 'application/x-www-form-urlencoded', // <-- Specifying the Content-Type
      }),
      body: base64image // <-- Post parameters
    })
      .then((response) => response.json())
      .then((responseJson) => {
        navigate("Map", {
          heading: heading,
          longitude: longitude,
          latitude: latitude,
          accuracy: accuracy,
          response: responseJson
        });
      })
      .catch((error) => {
        console.error(error);
      });
  }
}

class MapScreen extends BasicView {
  render() {
    const { navigation } = this.props;
    const { navigate } = this.props.navigation;
    const heading = navigation.getParam('heading', '');
    const longitude = navigation.getParam('longitude', 'Could not load');
    const latitude = navigation.getParam('latitude', 'Could not load');
    const accuracy = navigation.getParam('accuracy', 'Could not load');
    const response = navigation.getParam('response', '');
    return (
      <View style={{ flex: 1, alignItems: 'flex-start', justifyContent: "flex-start" }}>
        <Image style={{ width: 360, height: 480, marginTop: 0 }} source={{ uri: host + "/result.jpg" }} />
        <TouchableOpacity style={{ width: 340, paddingLeft: 10, paddingRight:10, alignItems: 'center', justifyContent: "center", flexDirection: 'column' }} onPress={() => { navigate("Home") }}>
          <View style={{ alignItems: 'center', justifyContent: "center", flexDirection: 'row', height: 40 }}>
            <View><Text>Lon: {longitude} </Text></View>
            <View><Text>Lat: {latitude} </Text></View>
            <View><Text>Acc: {accuracy} m</Text></View>
          </View>
          <View style={{ alignItems: 'center', justifyContent: "center", flexDirection: 'row', height: 40 }}>
            <View><Text>X axis angle: {response["theta"]} </Text></View>
            <View><Text>Heading: {heading} </Text></View>
            <View><Text>Y axis angle: {response["shear"]} </Text></View>
          </View>
        </TouchableOpacity>
      </View>
    );
  }
}

const styles = StyleSheet.create({
  maincontainer: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center'
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
  },
  parameters_box: {
    width: 120
  }
});

const RootStack = createStackNavigator(
  {
    Home: HomeScreen,
    PhotoTaker: PhotoTakerScreen,
    Map: MapScreen,
    Load: LoadingScreen
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