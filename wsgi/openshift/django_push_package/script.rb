#!/usr/bin/env ruby
require 'openssl'
require 'optparse'

# $> push_package --website-json=./website.json --iconset=~/project/iconset --certificate=./Certificate.p12 --output-dir=./
options = {}
options_parser = OptionParser.new do |opts|
  opts.banner = 'Usage: push_package [options]'
  opts.on('-t', '--tmpdir required', 'The path to the file containing the manifest.json') do |opt|
    options[:tmpdir] = opt
  end
end

options_parser.parse!

# check the required options
unless File.directory?(options[:tmpdir].to_s)
  puts options_parser.help
  exit 1
end

def write_signature(tmpdir)
  certificate = tmpdir + '/../cert.p12'
  cert_data = File.read(certificate)
  p12 = OpenSSL::PKCS12.new(cert_data, nil)
  manifest_data = File.read(tmpdir + '/manifest.json')
  signature = OpenSSL::PKCS7::sign(p12.certificate, p12.key, manifest_data, [], OpenSSL::PKCS7::BINARY | OpenSSL::PKCS7::DETACHED)
  File.open(tmpdir + '/signature', 'wb+') do |file|
    file.write(signature.to_der)
  end
end

write_signature(options[:tmpdir])
