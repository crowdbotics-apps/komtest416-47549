import { Picker } from "@react-native-picker/picker";
import React, { useEffect, useState } from "react";
import { Image, Pressable, SafeAreaView, ScrollView, StyleSheet, Text, View } from "react-native";
import { useDispatch, useSelector } from "react-redux";
import { api_add_admin_machine } from "@store/mykomatsuAPI/machine.slice";
import MyComponent from "@components/MyComponent.web";

const addMachine = ({
  route,
  navigation
}) => {
  const [modelName, setModelName] = useState("");
  const [selectedProduct, setSelectedProduct] = useState("");
  const [selectedCustomer, setSelectedCustomer] = useState("");
  const [selectedLocation, setSelectedLocation] = useState("");
  const [serial, setSerial] = useState("");
  const [unit, setUnit] = useState("");
  const [customerRef, setCustomerRef] = useState("");
  const dispatch = useDispatch();
  const [dimensions, setDimensions] = useState({
    height: window.innerHeight,
    width: window.innerWidth
  });
  useEffect(() => {
    function handleResize() {
      setDimensions({
        height: window.innerHeight,
        width: window.innerWidth
      });
    }

    window.addEventListener("resize", handleResize);
    return _ => {
      window.removeEventListener("resize", handleResize);
    };
  });
  const machine = useSelector(state => state.MachineDetails);
  return <SafeAreaView style={styles.TeClvrCy}>
      <ScrollView contentContainerStyle={styles.scrollView}>
        <View style={styles.group}>
          <View style={styles.XmlEekdR}>
            <Text style={styles.bIyQmvqX}>
              Add Machine
            </Text>
            <View style={styles.PVUYGECn}>
              <Image style={styles.logo} source={require("../../assets/images/cross_icon/cross_icon.png")} />
            </View>
          </View>
          <View style={styles.aYDnYJYT}>
            <View style={styles.uouHDSMg}>
              <View style={[styles.group]}>
                <Text style={styles.text}>Model Name *</Text>
                <MyComponent value={modelName} onChangeText={text => setModelName(text)} style={styles.OsnwxunM} />
              </View>
              <View style={styles.group}>
                <Text style={styles.text}>Product Type *</Text>
                <Picker selectedValue={selectedProduct} style={styles.LHOKLyqY} onValueChange={(itemValue, itemIndex) => setSelectedProduct(itemValue)}>
                  <Picker.Item label="CRAWLER DOZER" value="CRAWLER DOZER" />
                  <Picker.Item label="DOZER A" value="DOZER A" />
                  <Picker.Item label="CRAWLER B" value="CRAWLER B" />
                  <Picker.Item label="CONSUMER PRODUCT" value="CONSUMER PRODUCT" />
                </Picker>
              </View>
            </View>
            <View style={styles.ttCCIUYj}>
              <View style={styles.group}>
                <Text style={styles.text}>Customer *</Text>
                <Picker selectedValue={selectedCustomer} style={styles.kVUIMCYV} onValueChange={(itemValue, itemIndex) => setSelectedCustomer(itemValue)}>
                  <Picker.Item label="2COM Construction LLC" value="2COM Construction LLC" />
                  <Picker.Item label="VIOCOM Construction PVT LTD" value="VIOCOM Construction PVT LTD" />
                  <Picker.Item label="Construction Public Domain" value="Construction Public Domain" />
                  <Picker.Item label="PPV Construction INC" value="PPV Construction INC" />
                </Picker>
              </View>
              <View style={styles.group}>
                <Text style={styles.text}>Location *</Text>
                <Picker selectedValue={selectedLocation} style={styles.GSLZVWuj} onValueChange={(itemValue, itemIndex) => setSelectedLocation(itemValue)}>
                  <Picker.Item label="Main, Test New Location" value="Main, Test New Location" />
                  <Picker.Item label="East cost, villa road" value="East cost, villa road" />
                  <Picker.Item label="New york city" value="New york city" />
                  <Picker.Item label="Saa costa, river front" value="Saa costa, river front" />
                </Picker>
              </View>
            </View>
            <View style={styles.wudHzitD}>
              <View style={styles.FNbWnCSB}>
                <Text style={styles.text}>Serial # *</Text>
                <MyComponent value={serial} onChangeText={text => setSerial(text)} />
              </View>
              <View style={styles.fJjcQWOi}>
                <Text style={styles.text}>Unit #</Text>
                <MyComponent value={unit} onChangeText={text => setUnit(text)} />
              </View>
              <View style={styles.dggOcqFu}>
                <Text style={styles.text}>Customer Reference # *</Text>
                <MyComponent value={customerRef} onChangeText={text => setCustomerRef(text)} />
              </View>
            </View>
          </View>
        </View>
      </ScrollView>
      <View style={styles.dyZsfVqN}>
        <View style={styles.WDbhCNHI}>
          <View style={styles.UaXYzsrX}>
            <Pressable onPress={() => {
            dispatch(api_add_admin_machine({
              params: {
                model_name: modelName,
                product_type: selectedProduct,
                customer: selectedCustomer,
                location: selectedLocation,
                serial: serial,
                unit: unit,
                customer_referance: customerRef,
                status: "Included",
                matched: "Yes",
                actions: "Machine Registered Successfully"
              }
            }));
            setModelName("");
            setSelectedProduct("");
            setSelectedCustomer("");
            setSelectedLocation("");
            setSerial("");
            setUnit("");
            setCustomerRef("");
          }} style={({
            pressed
          }) => [{
            backgroundColor: pressed ? "light-blue" : "#131A94",
            height: 40,
            width: 90,
            marginRight: 20,
            borderColor: "white",
            borderWidth: 1,
            borderRadius: 4
          }]}>
              <Text style={styles.IIdykdqk}>
                Save
              </Text>
            </Pressable>
            <Pressable onPress={() => {
            navigation.navigate("addLocation");
          }} style={({
            pressed
          }) => [{
            backgroundColor: pressed ? "light-gray" : "white",
            height: 40,
            width: 90,
            marginRight: 20,
            borderColor: "#131A94",
            borderWidth: 1,
            borderRadius: 4
          }]}>
              <Text style={styles.urNHCznx}>
                Cancel
              </Text>
            </Pressable>
          </View>
        </View>
      </View>
    </SafeAreaView>;
};

const styles = StyleSheet.create({
  scrollView: {
    flex: 1,
    width: "100%",
    alignItems: "flex-start",
    justifyContent: "space-between",
    backgroundColor: "white"
  },
  group: {
    alignItems: "flex-start",
    width: "100%"
  },
  logo: {
    height: 25,
    width: 25,
    borderRadius: 30,
    alignSelf: "flex-end",
    marginRight: 10
  },
  text: {
    fontSize: 14,
    color: "#000000",
    fontWeight: "bold"
  },
  footer: {
    textAlign: "left",
    fontSize: 18,
    color: "#828AB0",
    fontWeight: 700,
    marginBottom: 20
  },
  input: {
    height: 40,
    margin: 12,
    borderWidth: 1,
    padding: 10
  },
  TeClvrCy: {
    flex: 1,
    width: "dimensions.width",
    height: "dimensions.height"
  },
  XmlEekdR: {
    backgroundColor: "#131A94",
    flexDirection: "row",
    paddingVertical: "hp",
    width: "dimensions.width"
  },
  bIyQmvqX: {
    color: "white",
    padding: "hp",
    fontSize: 16,
    marginLeft: 5,
    fontWeight: "bold"
  },
  PVUYGECn: {
    flex: 1
  },
  aYDnYJYT: {
    margin: 20
  },
  uouHDSMg: {
    flexDirection: "row",
    marginTop: 10
  },
  OsnwxunM: {
    width: 330
  },
  LHOKLyqY: {
    width: 330,
    marginTop: 10,
    height: 30,
    marginLeft: 10
  },
  ttCCIUYj: {
    flexDirection: "row",
    marginTop: 25
  },
  kVUIMCYV: {
    width: 330,
    marginTop: 10,
    height: 30
  },
  GSLZVWuj: {
    width: 330,
    marginTop: 10,
    height: 30,
    marginLeft: 10
  },
  wudHzitD: {
    flexDirection: "row",
    marginTop: 25
  },
  FNbWnCSB: {
    width: "60%"
  },
  fJjcQWOi: {
    width: "60%"
  },
  dggOcqFu: {
    width: "60%"
  },
  dyZsfVqN: {
    alignContent: "flex-end",
    width: "100%",
    backgroundColor: "light-gray",
    height: 70
  },
  WDbhCNHI: {
    flex: 1
  },
  UaXYzsrX: {
    flex: 1,
    flexDirection: "row-reverse",
    alignItems: "center"
  },
  IIdykdqk: {
    textAlign: "center",
    marginVertical: 10,
    color: "white"
  },
  urNHCznx: {
    textAlign: "center",
    marginVertical: 10,
    color: "#131A94"
  }
});
export default addMachine;