package main

import (
	"encoding/json"
	"fmt"

	"github.com/hyperledger/fabric/core/chaincode/shim"
	sc "github.com/hyperledger/fabric/protos/peer"
)

type SmartContract struct {
}

type bankStatement struct {
	Id string `json:"id"`
	Date string `json:"date"`
	Transaction string `json:"transaction"`
	Balance string `json:"balance"`
    AccountId string `json:"accountId"`
    Description string `json:"description"`
    ApproveStatus string `json:"approveStatus"`
}



func constructIdKey(product_id string) string {
	return fmt.Sprintf("id_%s", product_id)
}

func (s *SmartContract) Init(APIstub shim.ChaincodeStubInterface) sc.Response {
	return shim.Success(nil)
}

func (s *SmartContract) Invoke(APIstub shim.ChaincodeStubInterface) sc.Response {

	function, args := APIstub.GetFunctionAndParameters()

	switch function {
	case "createBankStatement":
		return createBankStatement(APIstub, args)
	case "getBankStatement":
		return getBankStatement(APIstub, args)
	default:
		return shim.Error("Invalid Smart Contract function name.")
	}
}

func createBankStatement(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {
	//检查参数个数
	if len(args) != 7 {
		return shim.Error("Incorrect number of arguments. Expecting 9")
	}

	//检查参数正确性
	id := args[0]
	date := args[1]
	transaction := args[2]
	balance := args[3]
	accountId := args[4]
	description := args[5]
	approveStatus := args[6]

	bankStatementData := &bankStatement{
		Id:             id,
		Date:           date,
		Transaction:    transaction,
		Balance:        balance,
		AccountId:		accountId,
		Description:	description,
		ApproveStatus:  approveStatus,
	}
	dataBytes, err := json.Marshal(bankStatementData)
	if err != nil {
		return shim.Error(fmt.Sprintf("marshal data error : %s", err))
	}

	datakey, err := APIstub.CreateCompositeKey("bankStatement_", []string{
		accountId,
		id,
	})
	if err != nil {
		return shim.Error(fmt.Sprintf("create key error: %s", err))
	}

	if err := APIstub.PutState(datakey, dataBytes); err != nil {
		return shim.Error(fmt.Sprintf("sava data error : %s", err))
	}

	fmt.Sprintf("createBankStatement Success")
	return shim.Success(nil)
}

func getBankStatement(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {
	//检查参数个数
	if len(args) != 1 {
		return shim.Error("Incorrect number of arguments. Expecting 1")
	}

	//验证参数是否正确
	accountId := args[0]
	if accountId == "" {
		return shim.Error("invalid args")
	}


	//查询数据
	keys := make([]string, 0)
	keys = append(keys, accountId)

	result, err := APIstub.GetStateByPartialCompositeKey("bankStatement_", keys)
	if err != nil {
		return shim.Error(fmt.Sprintf("query data error: %s", err))
	}
	defer result.Close()

	datas := make([]*bankStatement, 0)
	for result.HasNext() {
		dataVal, err := result.Next()
		if err != nil {
			return shim.Error(fmt.Sprintf("query error: %s", err))
		}

		data := new(bankStatement)
		if err := json.Unmarshal(dataVal.GetValue(), data); err != nil {
			return shim.Error(fmt.Sprintf("unmarshal error: %s", err))
		}

		datas = append(datas, data)
	}


	datasBytes, err := json.Marshal(datas)
	if err != nil {
		return shim.Error(fmt.Sprintf("marshal error : %s", err))
	}

	fmt.Println(string(datasBytes))

	return shim.Success(datasBytes);
}


func main() {
	err := shim.Start(new(SmartContract))
	if err != nil {
		fmt.Printf("Error creating new Smart Contract: %s", err)
	}
}
