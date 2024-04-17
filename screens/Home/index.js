import React from "react";
import { Text, View, ScrollView, StyleSheet } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import faker from "faker"; // Generate fake data using faker.

const fakeData = Array.from({
  length: 20
}, () => ({
  id: faker.datatype.uuid(),
  company: faker.company.companyName(0),
  name: faker.name.findName(),
  file: faker.system.commonFileName("csv")
}));

const App = () => {
  return <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        <View style={styles.navbar}>
          <Text style={styles.navbarTitle}>KomTest</Text>
        </View>
        <ScrollView contentContainerStyle={styles.contentContainer}>
          <Text style={styles.title}>Accounts</Text>
          {fakeData.map(item => <View key={item.id} style={styles.itemContainer}>
              <Text style={styles.big}>Distributor: {item.company}</Text>
              <Text style={styles.small}>File: {item.file}</Text>
              <Text style={styles.small}>Owner: {item.name}</Text>
            </View>)}
        </ScrollView>
      </View>
    </SafeAreaView>;
}; // Styles for the app components.


const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: "#f8f9fa"
  },
  container: {
    flex: 1
  },
  navbar: {
    height: 60,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#273d99",
    shadowOpacity: 0.2,
    shadowRadius: 5,
    shadowColor: "#000",
    shadowOffset: {
      height: 2,
      width: 0
    },
    elevation: 4 // for Android shadow effect

  },
  navbarTitle: {
    color: "white",
    fontSize: 24,
    fontWeight: "bold",
    fontFamily: "inherit"
  },
  contentContainer: {
    flexGrow: 1,
    alignItems: "center",
    padding: 20
  },
  title: {
    fontSize: 20,
    fontWeight: "bold",
    marginBottom: 20
  },
  itemContainer: {
    padding: 10,
    marginVertical: 5,
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 5,
    backgroundColor: "white",
    width: "100%"
  },
  big: {
    fontSize: 16,
    fontWeight: "bold"
  },
  other: {
    fontSize: 15
  },
  small: {
    fontSize: 14
  }
});
export default App;