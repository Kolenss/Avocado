import { View, Text } from 'react-native'

type Label ={
    label: string;
    className?: string
}

export default function Button1({ label, className }: Label){
    return(
        <>
            <View className={`border w-[103px] rounded-[50px] h-[25px] justify-center items-center ${ className }`}>
                <Text>
                    { label ? label : "Label"}
                </Text>
            </View>
        </>
    );
}