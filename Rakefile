require 'uri'

VERSION = "0.0.2"
PYTHON_ENVS = [:env27, :env33]
PYTHON_EXECS = {:env26 => "python2.6", :env27 => "python2.7", :env32 => "python3.2", :env33 => "python3.3"}

module OS
  def OS.windows?
    (/cygwin|mswin|mingw|bccwin|wince|emx/ =~ RUBY_PLATFORM) != nil
  end

  def OS.mac?
   (/darwin/ =~ RUBY_PLATFORM) != nil
  end

  def OS.unix?
    !OS.windows?
  end

  def OS.linux?
    OS.unix? and not OS.mac?
  end
end

def md5(source, target)
  require "digest/md5"
  md5 = Digest::MD5.hexdigest(File.read(source))
  File.open(target, 'w') { |file| file.write(md5) }
end

def colorize(text, color)
  color_codes = {
    :black    => 30,
    :red      => 31,
    :green    => 32,
    :yellow   => 33,
    :blue     => 34,
    :magenta  => 35,
    :cyan     => 36,
    :white    => 37
  }
  code = color_codes[color]
  if code == nil
    text
  else
    "\033[#{code}m#{text}\033[0m"
  end
end

def virtual_env(command, env="env33")
  sh "source #{env}/bin/activate && #{command}"
end

def create_virtual_env(dir, python)
  sh "virtualenv #{dir} -p #{python}"
end

task :clean => [] do
  sh "rm -rf ~*"
  sh "find . -name '*.pyc' -delete"
  sh "rm -rf data/"
  sh "rm -rf *.egg-info"
  sh "rm -rf dist/"
end

task :install => [] do
  sh "python --version"
  sh "ruby --version"
  sh "easy_install pip"
end

task :dev_env => [] do
  PYTHON_ENVS.each { |env|
    puts colorize("Environment #{env}", :blue)
    create_virtual_env(env, PYTHON_EXECS[env])
  }
end

task :dependencies => [:dev_env] do
  PYTHON_ENVS.each { |env|
    puts colorize("Environment #{env}", :blue)
    virtual_env("pip install -r requirements.txt", "#{env}")
    virtual_env("pip install -r requirements-test.txt", "#{env}")
  }
end

task :tests => [] do
  PYTHON_ENVS.each { |env|
    puts colorize("Environment #{env}", :blue)
    virtual_env("nosetests --process-timeout=3 --verbosity=2", env)
  }
end

task :tag => [:tests] do
  sh "git tag #{VERSION}"
  sh "git push origin #{VERSION}"
end

task :reset_tag => [] do
  sh "git tag -d #{VERSION}"
  sh "git push origin :refs/tags/#{VERSION}"
end

task :publish => [:tests, :tag] do
  # http://guide.python-distribute.org/quickstart.html
  # python setup.py sdist
  # python setup.py register
  # python setup.py sdist upload
  # Manual upload to PypI
  # http://pypi.python.org/pypi/THE-PROJECT
  # Go to 'edit' link
  # Update version and save
  # Go to 'files' link and upload the file
  virtual_env("python setup.py sdist upload")
end

DIST_DIR = 'dist'
PACKAGE_NAME = "gat-runner"
BUILD_DIR = "#{PACKAGE_NAME}-build"
VE_DIR = "env27/lib/python2.7/site-packages"
DEPENDENCIES = ['simplejson', 'six.py']
task :package do
  sh "rm -rf #{DIST_DIR}"
  sh "rm -rf #{BUILD_DIR}"
  sh "mkdir #{DIST_DIR}"
  sh "mkdir #{BUILD_DIR}"
  sh "touch #{BUILD_DIR}/__init__.py"
  sh "cp __main__.py #{BUILD_DIR}"
  sh "cp -R gat_games #{BUILD_DIR}"
  DEPENDENCIES.each { |dep|
    sh "cp -r #{VE_DIR}/#{dep} #{BUILD_DIR}"
  }
  sh "cd #{BUILD_DIR} && zip -r ../#{PACKAGE_NAME}.zip * && cd -" # tricky to __main__stay in the root directory
  sh "echo '#!/usr/bin/env python' | cat - #{PACKAGE_NAME}.zip > #{PACKAGE_NAME}"
  sh "chmod +x #{PACKAGE_NAME}"
  sh "mv #{PACKAGE_NAME}.zip #{BUILD_DIR}"
  sh "rm -rf #{BUILD_DIR}"
  sh "mv #{PACKAGE_NAME} #{DIST_DIR}"
  md5("#{DIST_DIR}/#{PACKAGE_NAME}", "#{DIST_DIR}/gat-runner.checksum.md5")
end

task :package_mac => [:package] do
  sh "zip -j #{DIST_DIR}/gat-runner-mac.zip #{DIST_DIR}/gat-runner package_files/*_mac*"
  md5("#{DIST_DIR}/#{PACKAGE_NAME}", "#{DIST_DIR}/gat-runner-mac.zip.checksum.md5")
end

task :package_linux => [:package] do
  sh "zip -j #{DIST_DIR}/gat-runner-linux.zip #{DIST_DIR}/gat-runner package_files/*_linux*"
  md5("#{DIST_DIR}/#{PACKAGE_NAME}", "#{DIST_DIR}/gat-runner-linux.zip.checksum.md5")
end

task :package_windows => [:package] do
  sh "zip -j #{DIST_DIR}/gat-runner-windows.zip #{DIST_DIR}/gat-runner package_files/*_windows*"
  md5("#{DIST_DIR}/#{PACKAGE_NAME}", "#{DIST_DIR}/gat-runner-windows.zip.checksum.md5")
end

task :packages => [:package_mac, :package_linux, :package_windows] do
  sh "cp VERSION #{DIST_DIR}/latest-version"
end

namespace :integration_tests do
  GAMES = [
    {:name => "Truco", :langs => [
      "https://raw.github.com/gatournament/gat-python/master/sample/truco.py",
      "https://raw.github.com/gatournament/gat-ruby/master/lib/sample/truco.rb",
      "https://raw.github.com/gatournament/gat-java/master/sample/Truco.java",
    ]},
    {:name => "TrucoCleanDeck", :langs => [
      "https://raw.github.com/gatournament/gat-python/master/sample/truco.py",
      "https://raw.github.com/gatournament/gat-ruby/master/lib/sample/truco.rb",
      "https://raw.github.com/gatournament/gat-java/master/sample/Truco.java",
    ]},
  ]

  DIR = "integration_tests/"

  task :prepare => [:packages] do
    sh "rm -rf #{DIR} && mkdir -p #{DIR}"

    puts colorize("Installing GAT-Runner", :blue)
    sh "cp ./dist/gat-runner #{DIR}"

    puts colorize("Installing dependencies", :blue)
    sh "cd #{DIR} && wget -qN https://oss.sonatype.org/content/groups/public/com/gatournament/gat-java/0.0.1/gat-java.jar"
    sh "gem install gat_ruby"
    sh "pip install gat-python"

    puts colorize("Downloading algorithms", :blue)
    GAMES.each { |game|
      game[:langs].each { |url|
        sh "cd #{DIR} && wget -qN #{url}"
      }
    }
  end

  task :run => [:packages] do
    puts colorize("Installing GAT-Runner", :blue)
    sh "mkdir -p #{DIR}"
    sh "cp ./dist/gat-runner #{DIR}"

    GAMES.each { |game|
      puts colorize("Testing game #{game[:name]}", :blue)
      langs = ["gat-random"]
      game[:langs].each { |url|
        filename = File.basename(URI.parse(url).path)
        langs << filename
      }
      combinations = langs.combination(2).to_a
      # puts combinations.inspect
      combinations.each { |combination|
        filename1 = combination[0]
        filename2 = combination[1]
        lang1 = File.extname(filename1).split(".").last
        lang2 = File.extname(filename2).split(".").last
        lang1 = "GATRandom" if not lang1 or lang1.empty?
        lang2 = "GATRandom" if not lang2 or lang2.empty?
        puts colorize("Running #{lang1} vs #{lang2}", :blue)
        sh "cd #{DIR} && ./gat-runner #{game[:name]} #{filename1} #{filename2} -n1 #{lang1} -n2 #{lang2} -ll 50 -d --no-replay"
      }
    }
  end

  task :all => [:packages, "integration_tests:prepare", :run]
end

def upload_to_s3(files, bucket_name)
  # rvm install 1.9.3
  # gem install aws-sdk
  require 'aws-sdk'
  puts colorize("Uploading to S3", :blue)
  AWS.config(access_key_id: ENV["AWS_ACCESS_KEY_ID"], secret_access_key: ENV["AWS_SECRET_ACCESS_KEY"], region: ENV["AWS_REGION"])
  bucket = AWS.s3.buckets[bucket_name]
  if not bucket.exists? then
    bucket = AWS.s3.buckets.create(bucket_name, :acl => :public_read)
    bucket.configure_website
  end
  files.each { |filename|
    key = File.basename(filename)
    obj = bucket.objects[key]
    obj.write(:file => filename, :acl => :public_read)
    puts obj.public_url
  }
  puts colorize("Upload finished", :green)
end

task :upload => [:packages] do
  OSs = ["mac", "linux", "windows"]
  files = []
  OSs.each { |os|
    zip = "#{DIST_DIR}/gat-runner-#{os}.zip"
    md5 = "#{DIST_DIR}/gat-runner-#{os}.zip.checksum.md5"
    files.push(zip)
    files.push(md5)
  }
  files.push("dist/latest-version")
  bucket = "gat-runner"
  upload_to_s3(files, bucket)
end

task :all => [:dev_env, :dependencies, :tests]

task :default => [:tests]
