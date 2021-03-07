# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: hfc/protos/orderer/configuration.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='hfc/protos/orderer/configuration.proto',
  package='orderer',
  syntax='proto3',
  serialized_options=b'\n%org.hyperledger.fabric.protos.ordererZ/github.com/hyperledger/fabric-protos-go/orderer',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n&hfc/protos/orderer/configuration.proto\x12\x07orderer\"\x8e\x01\n\rConsensusType\x12\x0c\n\x04type\x18\x01 \x01(\t\x12\x10\n\x08metadata\x18\x02 \x01(\x0c\x12+\n\x05state\x18\x03 \x01(\x0e\x32\x1c.orderer.ConsensusType.State\"0\n\x05State\x12\x10\n\x0cSTATE_NORMAL\x10\x00\x12\x15\n\x11STATE_MAINTENANCE\x10\x01\"_\n\tBatchSize\x12\x19\n\x11max_message_count\x18\x01 \x01(\r\x12\x1a\n\x12\x61\x62solute_max_bytes\x18\x02 \x01(\r\x12\x1b\n\x13preferred_max_bytes\x18\x03 \x01(\r\"\x1f\n\x0c\x42\x61tchTimeout\x12\x0f\n\x07timeout\x18\x01 \x01(\t\"\x1f\n\x0cKafkaBrokers\x12\x0f\n\x07\x62rokers\x18\x01 \x03(\t\"(\n\x13\x43hannelRestrictions\x12\x11\n\tmax_count\x18\x01 \x01(\x04\x42X\n%org.hyperledger.fabric.protos.ordererZ/github.com/hyperledger/fabric-protos-go/ordererb\x06proto3'
)



_CONSENSUSTYPE_STATE = _descriptor.EnumDescriptor(
  name='State',
  full_name='orderer.ConsensusType.State',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='STATE_NORMAL', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='STATE_MAINTENANCE', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=146,
  serialized_end=194,
)
_sym_db.RegisterEnumDescriptor(_CONSENSUSTYPE_STATE)


_CONSENSUSTYPE = _descriptor.Descriptor(
  name='ConsensusType',
  full_name='orderer.ConsensusType',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='orderer.ConsensusType.type', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='metadata', full_name='orderer.ConsensusType.metadata', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='state', full_name='orderer.ConsensusType.state', index=2,
      number=3, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _CONSENSUSTYPE_STATE,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=52,
  serialized_end=194,
)


_BATCHSIZE = _descriptor.Descriptor(
  name='BatchSize',
  full_name='orderer.BatchSize',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='max_message_count', full_name='orderer.BatchSize.max_message_count', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='absolute_max_bytes', full_name='orderer.BatchSize.absolute_max_bytes', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='preferred_max_bytes', full_name='orderer.BatchSize.preferred_max_bytes', index=2,
      number=3, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
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
  serialized_start=196,
  serialized_end=291,
)


_BATCHTIMEOUT = _descriptor.Descriptor(
  name='BatchTimeout',
  full_name='orderer.BatchTimeout',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='timeout', full_name='orderer.BatchTimeout.timeout', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
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
  serialized_start=293,
  serialized_end=324,
)


_KAFKABROKERS = _descriptor.Descriptor(
  name='KafkaBrokers',
  full_name='orderer.KafkaBrokers',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='brokers', full_name='orderer.KafkaBrokers.brokers', index=0,
      number=1, type=9, cpp_type=9, label=3,
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
  serialized_start=326,
  serialized_end=357,
)


_CHANNELRESTRICTIONS = _descriptor.Descriptor(
  name='ChannelRestrictions',
  full_name='orderer.ChannelRestrictions',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='max_count', full_name='orderer.ChannelRestrictions.max_count', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
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
  serialized_start=359,
  serialized_end=399,
)

_CONSENSUSTYPE.fields_by_name['state'].enum_type = _CONSENSUSTYPE_STATE
_CONSENSUSTYPE_STATE.containing_type = _CONSENSUSTYPE
DESCRIPTOR.message_types_by_name['ConsensusType'] = _CONSENSUSTYPE
DESCRIPTOR.message_types_by_name['BatchSize'] = _BATCHSIZE
DESCRIPTOR.message_types_by_name['BatchTimeout'] = _BATCHTIMEOUT
DESCRIPTOR.message_types_by_name['KafkaBrokers'] = _KAFKABROKERS
DESCRIPTOR.message_types_by_name['ChannelRestrictions'] = _CHANNELRESTRICTIONS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ConsensusType = _reflection.GeneratedProtocolMessageType('ConsensusType', (_message.Message,), {
  'DESCRIPTOR' : _CONSENSUSTYPE,
  '__module__' : 'hfc.protos.orderer.configuration_pb2'
  # @@protoc_insertion_point(class_scope:orderer.ConsensusType)
  })
_sym_db.RegisterMessage(ConsensusType)

BatchSize = _reflection.GeneratedProtocolMessageType('BatchSize', (_message.Message,), {
  'DESCRIPTOR' : _BATCHSIZE,
  '__module__' : 'hfc.protos.orderer.configuration_pb2'
  # @@protoc_insertion_point(class_scope:orderer.BatchSize)
  })
_sym_db.RegisterMessage(BatchSize)

BatchTimeout = _reflection.GeneratedProtocolMessageType('BatchTimeout', (_message.Message,), {
  'DESCRIPTOR' : _BATCHTIMEOUT,
  '__module__' : 'hfc.protos.orderer.configuration_pb2'
  # @@protoc_insertion_point(class_scope:orderer.BatchTimeout)
  })
_sym_db.RegisterMessage(BatchTimeout)

KafkaBrokers = _reflection.GeneratedProtocolMessageType('KafkaBrokers', (_message.Message,), {
  'DESCRIPTOR' : _KAFKABROKERS,
  '__module__' : 'hfc.protos.orderer.configuration_pb2'
  # @@protoc_insertion_point(class_scope:orderer.KafkaBrokers)
  })
_sym_db.RegisterMessage(KafkaBrokers)

ChannelRestrictions = _reflection.GeneratedProtocolMessageType('ChannelRestrictions', (_message.Message,), {
  'DESCRIPTOR' : _CHANNELRESTRICTIONS,
  '__module__' : 'hfc.protos.orderer.configuration_pb2'
  # @@protoc_insertion_point(class_scope:orderer.ChannelRestrictions)
  })
_sym_db.RegisterMessage(ChannelRestrictions)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
