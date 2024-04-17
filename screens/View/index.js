import React from "react";
  import { View, StyleSheet, ScrollView, SafeAreaView } from "react-native";

  const View = () => {
    return (
      <SafeAreaView style={styles.safeArea}>
        <ScrollView contentContainerStyle={{
          backgroundColor: '#f0f0f1',
          padding: 10,
          position: 'relative',
          flex: 1
        }}></ScrollView>
    </SafeAreaView>
    )};

    const styles = StyleSheet.create({
      safeArea: {
        height:'100%'
      },
    });

  export default View;