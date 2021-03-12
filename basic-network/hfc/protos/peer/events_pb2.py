# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: hfc/protos/peer/events.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from hfc.protos.common import common_pb2 as hfc_dot_protos_dot_common_dot_common__pb2
from hfc.protos.ledger.rwset import rwset_pb2 as hfc_dot_protos_dot_ledger_dot_rwset_dot_rwset__pb2
from hfc.protos.peer import chaincode_event_pb2 as hfc_dot_protos_dot_peer_dot_chaincode__event__pb2
from hfc.protos.peer import transaction_pb2 as hfc_dot_protos_dot_peer_dot_transaction__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='hfc/protos/peer/events.proto',
  package='protos',
  syntax='proto3',
  serialized_options=b'\n\"org.hyperledger.fabric.protos.peerB\rEventsPackageZ,github.com/hyperledger/fabric-protos-go/peer',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x1chfc/protos/peer/events.proto\x12\x06protos\x1a\x1ehfc/protos/common/common.proto\x1a#hfc/protos/ledger/rwset/rwset.proto\x1a%hfc/protos/peer/chaincode_event.proto\x1a!hfc/protos/peer/transaction.proto\"o\n\rFilteredBlock\x12\x12\n\nchannel_id\x18\x01 \x01(\t\x12\x0e\n\x06number\x18\x02 \x01(\x04\x12:\n\x15\x66iltered_transactions\x18\x04 \x03(\x0b\x32\x1b.protos.FilteredTransaction\"\xc6\x01\n\x13\x46ilteredTransaction\x12\x0c\n\x04txid\x18\x01 \x01(\t\x12 \n\x04type\x18\x02 \x01(\x0e\x32\x12.common.HeaderType\x12\x34\n\x12tx_validation_code\x18\x03 \x01(\x0e\x32\x18.protos.TxValidationCode\x12\x41\n\x13transaction_actions\x18\x04 \x01(\x0b\x32\".protos.FilteredTransactionActionsH\x00\x42\x06\n\x04\x44\x61ta\"X\n\x1a\x46ilteredTransactionActions\x12:\n\x11\x63haincode_actions\x18\x01 \x03(\x0b\x32\x1f.protos.FilteredChaincodeAction\"J\n\x17\x46ilteredChaincodeAction\x12/\n\x0f\x63haincode_event\x18\x01 \x01(\x0b\x32\x16.protos.ChaincodeEvent\"\xcf\x01\n\x13\x42lockAndPrivateData\x12\x1c\n\x05\x62lock\x18\x01 \x01(\x0b\x32\r.common.Block\x12I\n\x10private_data_map\x18\x02 \x03(\x0b\x32/.protos.BlockAndPrivateData.PrivateDataMapEntry\x1aO\n\x13PrivateDataMapEntry\x12\x0b\n\x03key\x18\x01 \x01(\x04\x12\'\n\x05value\x18\x02 \x01(\x0b\x32\x18.rwset.TxPvtReadWriteSet:\x02\x38\x01\"\xcb\x01\n\x0f\x44\x65liverResponse\x12 \n\x06status\x18\x01 \x01(\x0e\x32\x0e.common.StatusH\x00\x12\x1e\n\x05\x62lock\x18\x02 \x01(\x0b\x32\r.common.BlockH\x00\x12/\n\x0e\x66iltered_block\x18\x03 \x01(\x0b\x32\x15.protos.FilteredBlockH\x00\x12=\n\x16\x62lock_and_private_data\x18\x04 \x01(\x0b\x32\x1b.protos.BlockAndPrivateDataH\x00\x42\x06\n\x04Type2\xd4\x01\n\x07\x44\x65liver\x12:\n\x07\x44\x65liver\x12\x10.common.Envelope\x1a\x17.protos.DeliverResponse\"\x00(\x01\x30\x01\x12\x42\n\x0f\x44\x65liverFiltered\x12\x10.common.Envelope\x1a\x17.protos.DeliverResponse\"\x00(\x01\x30\x01\x12I\n\x16\x44\x65liverWithPrivateData\x12\x10.common.Envelope\x1a\x17.protos.DeliverResponse\"\x00(\x01\x30\x01\x42\x61\n\"org.hyperledger.fabric.protos.peerB\rEventsPackageZ,github.com/hyperledger/fabric-protos-go/peerb\x06proto3'
  ,
  dependencies=[hfc_dot_protos_dot_common_dot_common__pb2.DESCRIPTOR,hfc_dot_protos_dot_ledger_dot_rwset_dot_rwset__pb2.DESCRIPTOR,hfc_dot_protos_dot_peer_dot_chaincode__event__pb2.DESCRIPTOR,hfc_dot_protos_dot_peer_dot_transaction__pb2.DESCRIPTOR,])




_FILTEREDBLOCK = _descriptor.Descriptor(
  name='FilteredBlock',
  full_name='protos.FilteredBlock',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='channel_id', full_name='protos.FilteredBlock.channel_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='number', full_name='protos.FilteredBlock.number', index=1,
      number=2, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='filtered_transactions', full_name='protos.FilteredBlock.filtered_transactions', index=2,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=183,
  serialized_end=294,
)


_FILTEREDTRANSACTION = _descriptor.Descriptor(
  name='FilteredTransaction',
  full_name='protos.FilteredTransaction',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='txid', full_name='protos.FilteredTransaction.txid', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='type', full_name='protos.FilteredTransaction.type', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='tx_validation_code', full_name='protos.FilteredTransaction.tx_validation_code', index=2,
      number=3, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='transaction_actions', full_name='protos.FilteredTransaction.transaction_actions', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='Data', full_name='protos.FilteredTransaction.Data',
      index=0, containing_type=None,
      create_key=_descriptor._internal_create_key,
    fields=[]),
  ],
  serialized_start=297,
  serialized_end=495,
)


_FILTEREDTRANSACTIONACTIONS = _descriptor.Descriptor(
  name='FilteredTransactionActions',
  full_name='protos.FilteredTransactionActions',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='chaincode_actions', full_name='protos.FilteredTransactionActions.chaincode_actions', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=497,
  serialized_end=585,
)


_FILTEREDCHAINCODEACTION = _descriptor.Descriptor(
  name='FilteredChaincodeAction',
  full_name='protos.FilteredChaincodeAction',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='chaincode_event', full_name='protos.FilteredChaincodeAction.chaincode_event', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=587,
  serialized_end=661,
)


_BLOCKANDPRIVATEDATA_PRIVATEDATAMAPENTRY = _descriptor.Descriptor(
  name='PrivateDataMapEntry',
  full_name='protos.BlockAndPrivateData.PrivateDataMapEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='protos.BlockAndPrivateData.PrivateDataMapEntry.key', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='protos.BlockAndPrivateData.PrivateDataMapEntry.value', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'8\001',
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=792,
  serialized_end=871,
)

_BLOCKANDPRIVATEDATA = _descriptor.Descriptor(
  name='BlockAndPrivateData',
  full_name='protos.BlockAndPrivateData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='block', full_name='protos.BlockAndPrivateData.block', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='private_data_map', full_name='protos.BlockAndPrivateData.private_data_map', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_BLOCKANDPRIVATEDATA_PRIVATEDATAMAPENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=664,
  serialized_end=871,
)


_DELIVERRESPONSE = _descriptor.Descriptor(
  name='DeliverResponse',
  full_name='protos.DeliverResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='protos.DeliverResponse.status', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='block', full_name='protos.DeliverResponse.block', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='filtered_block', full_name='protos.DeliverResponse.filtered_block', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='block_and_private_data', full_name='protos.DeliverResponse.block_and_private_data', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='Type', full_name='protos.DeliverResponse.Type',
      index=0, containing_type=None,
      create_key=_descriptor._internal_create_key,
    fields=[]),
  ],
  serialized_start=874,
  serialized_end=1077,
)

_FILTEREDBLOCK.fields_by_name['filtered_transactions'].message_type = _FILTEREDTRANSACTION
_FILTEREDTRANSACTION.fields_by_name['type'].enum_type = hfc_dot_protos_dot_common_dot_common__pb2._HEADERTYPE
_FILTEREDTRANSACTION.fields_by_name['tx_validation_code'].enum_type = hfc_dot_protos_dot_peer_dot_transaction__pb2._TXVALIDATIONCODE
_FILTEREDTRANSACTION.fields_by_name['transaction_actions'].message_type = _FILTEREDTRANSACTIONACTIONS
_FILTEREDTRANSACTION.oneofs_by_name['Data'].fields.append(
  _FILTEREDTRANSACTION.fields_by_name['transaction_actions'])
_FILTEREDTRANSACTION.fields_by_name['transaction_actions'].containing_oneof = _FILTEREDTRANSACTION.oneofs_by_name['Data']
_FILTEREDTRANSACTIONACTIONS.fields_by_name['chaincode_actions'].message_type = _FILTEREDCHAINCODEACTION
_FILTEREDCHAINCODEACTION.fields_by_name['chaincode_event'].message_type = hfc_dot_protos_dot_peer_dot_chaincode__event__pb2._CHAINCODEEVENT
_BLOCKANDPRIVATEDATA_PRIVATEDATAMAPENTRY.fields_by_name['value'].message_type = hfc_dot_protos_dot_ledger_dot_rwset_dot_rwset__pb2._TXPVTREADWRITESET
_BLOCKANDPRIVATEDATA_PRIVATEDATAMAPENTRY.containing_type = _BLOCKANDPRIVATEDATA
_BLOCKANDPRIVATEDATA.fields_by_name['block'].message_type = hfc_dot_protos_dot_common_dot_common__pb2._BLOCK
_BLOCKANDPRIVATEDATA.fields_by_name['private_data_map'].message_type = _BLOCKANDPRIVATEDATA_PRIVATEDATAMAPENTRY
_DELIVERRESPONSE.fields_by_name['status'].enum_type = hfc_dot_protos_dot_common_dot_common__pb2._STATUS
_DELIVERRESPONSE.fields_by_name['block'].message_type = hfc_dot_protos_dot_common_dot_common__pb2._BLOCK
_DELIVERRESPONSE.fields_by_name['filtered_block'].message_type = _FILTEREDBLOCK
_DELIVERRESPONSE.fields_by_name['block_and_private_data'].message_type = _BLOCKANDPRIVATEDATA
_DELIVERRESPONSE.oneofs_by_name['Type'].fields.append(
  _DELIVERRESPONSE.fields_by_name['status'])
_DELIVERRESPONSE.fields_by_name['status'].containing_oneof = _DELIVERRESPONSE.oneofs_by_name['Type']
_DELIVERRESPONSE.oneofs_by_name['Type'].fields.append(
  _DELIVERRESPONSE.fields_by_name['block'])
_DELIVERRESPONSE.fields_by_name['block'].containing_oneof = _DELIVERRESPONSE.oneofs_by_name['Type']
_DELIVERRESPONSE.oneofs_by_name['Type'].fields.append(
  _DELIVERRESPONSE.fields_by_name['filtered_block'])
_DELIVERRESPONSE.fields_by_name['filtered_block'].containing_oneof = _DELIVERRESPONSE.oneofs_by_name['Type']
_DELIVERRESPONSE.oneofs_by_name['Type'].fields.append(
  _DELIVERRESPONSE.fields_by_name['block_and_private_data'])
_DELIVERRESPONSE.fields_by_name['block_and_private_data'].containing_oneof = _DELIVERRESPONSE.oneofs_by_name['Type']
DESCRIPTOR.message_types_by_name['FilteredBlock'] = _FILTEREDBLOCK
DESCRIPTOR.message_types_by_name['FilteredTransaction'] = _FILTEREDTRANSACTION
DESCRIPTOR.message_types_by_name['FilteredTransactionActions'] = _FILTEREDTRANSACTIONACTIONS
DESCRIPTOR.message_types_by_name['FilteredChaincodeAction'] = _FILTEREDCHAINCODEACTION
DESCRIPTOR.message_types_by_name['BlockAndPrivateData'] = _BLOCKANDPRIVATEDATA
DESCRIPTOR.message_types_by_name['DeliverResponse'] = _DELIVERRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

FilteredBlock = _reflection.GeneratedProtocolMessageType('FilteredBlock', (_message.Message,), {
  'DESCRIPTOR' : _FILTEREDBLOCK,
  '__module__' : 'hfc.protos.peer.events_pb2'
  # @@protoc_insertion_point(class_scope:protos.FilteredBlock)
  })
_sym_db.RegisterMessage(FilteredBlock)

FilteredTransaction = _reflection.GeneratedProtocolMessageType('FilteredTransaction', (_message.Message,), {
  'DESCRIPTOR' : _FILTEREDTRANSACTION,
  '__module__' : 'hfc.protos.peer.events_pb2'
  # @@protoc_insertion_point(class_scope:protos.FilteredTransaction)
  })
_sym_db.RegisterMessage(FilteredTransaction)

FilteredTransactionActions = _reflection.GeneratedProtocolMessageType('FilteredTransactionActions', (_message.Message,), {
  'DESCRIPTOR' : _FILTEREDTRANSACTIONACTIONS,
  '__module__' : 'hfc.protos.peer.events_pb2'
  # @@protoc_insertion_point(class_scope:protos.FilteredTransactionActions)
  })
_sym_db.RegisterMessage(FilteredTransactionActions)

FilteredChaincodeAction = _reflection.GeneratedProtocolMessageType('FilteredChaincodeAction', (_message.Message,), {
  'DESCRIPTOR' : _FILTEREDCHAINCODEACTION,
  '__module__' : 'hfc.protos.peer.events_pb2'
  # @@protoc_insertion_point(class_scope:protos.FilteredChaincodeAction)
  })
_sym_db.RegisterMessage(FilteredChaincodeAction)

BlockAndPrivateData = _reflection.GeneratedProtocolMessageType('BlockAndPrivateData', (_message.Message,), {

  'PrivateDataMapEntry' : _reflection.GeneratedProtocolMessageType('PrivateDataMapEntry', (_message.Message,), {
    'DESCRIPTOR' : _BLOCKANDPRIVATEDATA_PRIVATEDATAMAPENTRY,
    '__module__' : 'hfc.protos.peer.events_pb2'
    # @@protoc_insertion_point(class_scope:protos.BlockAndPrivateData.PrivateDataMapEntry)
    })
  ,
  'DESCRIPTOR' : _BLOCKANDPRIVATEDATA,
  '__module__' : 'hfc.protos.peer.events_pb2'
  # @@protoc_insertion_point(class_scope:protos.BlockAndPrivateData)
  })
_sym_db.RegisterMessage(BlockAndPrivateData)
_sym_db.RegisterMessage(BlockAndPrivateData.PrivateDataMapEntry)

DeliverResponse = _reflection.GeneratedProtocolMessageType('DeliverResponse', (_message.Message,), {
  'DESCRIPTOR' : _DELIVERRESPONSE,
  '__module__' : 'hfc.protos.peer.events_pb2'
  # @@protoc_insertion_point(class_scope:protos.DeliverResponse)
  })
_sym_db.RegisterMessage(DeliverResponse)


DESCRIPTOR._options = None
_BLOCKANDPRIVATEDATA_PRIVATEDATAMAPENTRY._options = None

_DELIVER = _descriptor.ServiceDescriptor(
  name='Deliver',
  full_name='protos.Deliver',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=1080,
  serialized_end=1292,
  methods=[
  _descriptor.MethodDescriptor(
    name='Deliver',
    full_name='protos.Deliver.Deliver',
    index=0,
    containing_service=None,
    input_type=hfc_dot_protos_dot_common_dot_common__pb2._ENVELOPE,
    output_type=_DELIVERRESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='DeliverFiltered',
    full_name='protos.Deliver.DeliverFiltered',
    index=1,
    containing_service=None,
    input_type=hfc_dot_protos_dot_common_dot_common__pb2._ENVELOPE,
    output_type=_DELIVERRESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='DeliverWithPrivateData',
    full_name='protos.Deliver.DeliverWithPrivateData',
    index=2,
    containing_service=None,
    input_type=hfc_dot_protos_dot_common_dot_common__pb2._ENVELOPE,
    output_type=_DELIVERRESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_DELIVER)

DESCRIPTOR.services_by_name['Deliver'] = _DELIVER

# @@protoc_insertion_point(module_scope)