import { View, Text } from 'react-native'

export default function InformationalCard({ information, className, logo }: any){
    return(
        <>
            <View  className={`w-[300px] flex flex-row items-center rounded-[10px] p-[15px] g-[5px] bg-lightgreenbg m-[5px] ${ className }`}>
                <Text className='h-[25]'>{ logo }   </Text>
                <Text className='items-center flex flex-row justify-center  '>
                    { information }
                </Text>
            </View>
        </>
    );
}
