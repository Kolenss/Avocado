import { Modal, View } from "react-native";
import { BlurView } from "expo-blur";
import CardModal from "./CardModal";



export default function SensorModal({ logo, Title, sensorModel, currentReading, setTab }: any){
    return(<>
        <Modal transparent={true} animationType='fade'>
            <BlurView className='flex-1' intensity={ 360 } tint='extraLight'>
                <View className=' flex-1 justify-center items-center '>
                    <CardModal logo={ logo } Title={ Title } sensorModel={ sensorModel } currentReading={ currentReading } setTab={ setTab } />
                </View>
            </BlurView>
        </Modal>
    </>);
}